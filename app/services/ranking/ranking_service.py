from __future__ import annotations


from math import exp, log1p
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
from collections import Counter

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func

from ...models import Article, ArticleCategory
from ...config.settings import settings
from .ranking_config import RankingConfig
from .ranking_features import (
    recency_score as _base_recency_score,
    length_score as _base_length_score,
    category_boost as _base_category_boost,
)
import os

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None


# ============================================================
# CONFIGURATION (moved to ranking_config.RankingConfig)
# ============================================================


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _recency_score(published_at: Optional[datetime], half_life_h: float) -> float:
    return _base_recency_score(published_at, half_life_h)


def _length_score(content: Optional[str], min_chars: int, target_chars: int) -> float:
    # retain slight log-scaling while reusing base component
    base = _base_length_score(content, min_chars, target_chars)
    return base


def _category_boost(cat: Optional[ArticleCategory], boosts: Dict[str, float]) -> float:
    return _base_category_boost(cat, boosts)


# ============================================================
# NEW COMPONENTS: ENTITY & TOPIC BOOST
# ============================================================

def _entity_boost(article: Article) -> float:
    """
    Compute entity influence boost based on extracted entities or known titles.
    If no NLP metadata exists, returns 0.
    """
    entities = getattr(article, "entities", None)  # e.g. ["Sushila Karki", "Prime Minister"]
    if not entities:
        return 0.0

    boost = 0.0
    for ent in entities:
        name = ent.lower()
        if any(k in name for k in ["prime minister", "president", "chief justice", "pm"]):
            boost += 0.15
        elif any(k in name for k in ["minister", "mayor", "ambassador", "ceo", "chairperson"]):
            boost += 0.10
        elif any(k in name for k in ["activist", "protester", "student leader"]):
            boost += 0.07
        elif any(k in name for k in ["organization", "ngo", "party"]):
            boost += 0.05
        else:
            boost += 0.03  # unknown entity still gets minor influence
    return min(boost, 0.25)  # cap


def _topic_boost(db: Session, article: Article, hours: int = 24) -> float:
    """
    Checks how frequent key terms or tags appear in recent articles.
    Requires article.keywords or tags field (list of strings).
    """
    # If schema lacks keywords, skip
    if not hasattr(Article, "keywords"):
        return 0.0
    tags = getattr(article, "keywords", None)
    if not tags:
        return 0.0

    cutoff = _now() - timedelta(hours=hours)
    stmt = select(Article.keywords).where(Article.published_at >= cutoff)
    rows = db.execute(stmt).scalars().all()

    all_terms = [term for row in rows if row for term in row]
    freq = Counter(all_terms)

    # Take average frequency of this article's tags
    counts = [freq.get(t, 0) for t in tags]
    if not counts:
        return 0.0
    avg_freq = sum(counts) / len(counts)
    return min(0.25, log1p(avg_freq) * 0.1)


# ============================================================
# COMPOSITE SCORING
# ============================================================

def compute_score(article: Article, db: Session, cfg: RankingConfig) -> Dict[str, Any]:
    recency = _recency_score(article.published_at, cfg.recency_half_life_hours)
    rel = float(article.reliability or 0.0)
    length = _length_score(article.content, cfg.min_content_chars, cfg.target_content_chars)
    cboost = _category_boost(getattr(article, "category", None), cfg.category_boosts)
    eboost = _entity_boost(article)
    tboost = _topic_boost(db, article)

    raw = (
        cfg.w_recency * recency
        + cfg.w_reliability * (rel ** 1.2)
        + cfg.w_length * length
        + cfg.w_category * cboost
        + cfg.w_entity * eboost
        + cfg.w_topic * tboost
    )

    # Decay penalty for too-old articles
    age_h = None
    if article.published_at:
        ts = article.published_at if article.published_at.tzinfo else article.published_at.replace(tzinfo=timezone.utc)
        age_h = (_now() - ts).total_seconds() / 3600.0
    if age_h is not None and age_h > cfg.max_age_hours:
        raw *= 0.5

    return {
        "score": round(float(raw), 6),
        "recency": round(recency, 4),
        "reliability": round(rel, 4),
        "length": round(length, 4),
        "category_boost": round(cboost, 4),
        "entity_boost": round(eboost, 4),
        "topic_boost": round(tboost, 4),
    }


# ============================================================
# MAIN RANKING PIPELINE
# ============================================================

def rank_articles(
    db: Session,
    *,
    cfg: Optional[RankingConfig] = None,
    top_n: int = 50,
    since_hours: Optional[int] = None,
    require_summary: bool = False,
) -> List[Dict[str, Any]]:
    cfg = cfg or RankingConfig()

    max_age = since_hours if since_hours is not None else cfg.max_age_hours
    cutoff = _now() - timedelta(hours=max_age)

    conditions = [Article.published_at >= cutoff]
    if require_summary:
        conditions += [Article.summary != None, Article.summary != ""]

    stmt = (
        select(Article)
        .where(and_(*conditions))
        .order_by(Article.published_at.desc())
        .limit(cfg.max_candidates)
    )

    articles = db.execute(stmt).scalars().all()

    ranked = []
    for a in articles:
        breakdown = compute_score(a, db, cfg)
        ranked.append({"article": a, "score": breakdown["score"], "breakdown": breakdown})

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked[:top_n]


def feature_set(
    db: Session,
    *,
    cfg: Optional[RankingConfig] = None,
    top_n: int = 10,
    since_hours: Optional[int] = None,
    require_summary: bool = True,
) -> List[Article]:
    ranked = rank_articles(db, cfg=cfg, top_n=top_n, since_hours=since_hours, require_summary=require_summary)
    return [r["article"] for r in ranked]


# ============================================================
# REDIS INTEGRATION FOR REALTIME RANK CACHING
# ============================================================

def record_article_rank(
    article: Article,
    db: Session,
    *,
    cfg: Optional[RankingConfig] = None,
    redis_url: Optional[str] = None,
    redis_key: str = "news:rank:recent",
) -> Optional[float]:
    """
    Compute the score and push to a Redis sorted set for quick retrieval.
    Member is article.id (UUID as string). Returns the score or None if unavailable.
    """
    cfg = cfg or RankingConfig()
    if redis is None:
        return None
    url = redis_url or settings.redis_url
    if not url:
        return None
    try:
        r = redis.from_url(url)
        breakdown = compute_score(article, db, cfg)
        score = float(breakdown["score"])
        r.zadd(redis_key, {str(article.id): score})
        return score
    except Exception:
        return None
