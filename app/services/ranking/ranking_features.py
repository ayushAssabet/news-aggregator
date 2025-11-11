from __future__ import annotations

from datetime import datetime, timezone
from math import exp
from typing import Optional, Dict

from ...models import ArticleCategory


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def recency_score(published_at: Optional[datetime], half_life_h: float) -> float:
    if not published_at:
        return 0.0
    try:
        ts = published_at if published_at.tzinfo else published_at.replace(tzinfo=timezone.utc)
    except Exception:
        return 0.0
    age_h = max(0.0, (now_utc() - ts).total_seconds() / 3600.0)
    if half_life_h <= 0:
        return 0.0
    return float(exp(-age_h / half_life_h))


def length_score(content: Optional[str], min_chars: int, target_chars: int) -> float:
    if not content:
        return 0.0
    n = len(content.strip())
    if n <= 0:
        return 0.0
    if n < min_chars:
        return max(0.0, n / float(min_chars)) * 0.4
    return min(1.0, n / float(target_chars))


def category_boost(cat: Optional[ArticleCategory], boosts: Dict[str, float]) -> float:
    if not cat:
        return 0.0
    try:
        name = cat.name
    except Exception:
        return 0.0
    return float(boosts.get(name, 0.0))
