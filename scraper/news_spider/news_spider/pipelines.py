from __future__ import annotations

import os
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy import select, bindparam
from sqlalchemy.orm import Session
from twisted.internet.threads import deferToThread
from pgvector.sqlalchemy import Vector
from pgvector import vector as pgvector  # ✅ direct vector helper

from app.database.db import SessionLocal, engine
from app.repositories import article_repository as repo
from app.models import Article
from app.services.summarize.summarize_service import generate_summary
from app.services.embedding.model_provider import embed_text
from app.services.trending import trending_engine
from app.config.settings import settings


class StoreArticlePipeline:
    """Scrapy pipeline that stores and deduplicates news articles in Postgres."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url

    # --- Scrapy lifecycle methods ---

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings.database_url)

    def open_spider(self, spider):
        if settings.enable_auto_create_tables:
            try:
                from app.database.base import Base
                Base.metadata.create_all(engine)
            except Exception as e:
                spider.logger.warning(f"Auto table creation skipped: {e}")
        self.Session = SessionLocal

    # --- Core logic ---

    def process_item(self, item, spider):
        return deferToThread(self._persist_item, dict(item), spider)

    def _persist_item(self, item: dict[str, Any], spider) -> dict[str, Any]:
        s: Session = self.Session()
        try:
            url = item.get("url")
            if not url:
                spider.logger.warning("Skipping item without URL")
                return item

            if repo.get_by_url(s, str(url)):
                spider.logger.debug(f"Duplicate URL skipped: {url}")
                return item

            title = item.get("title") or ""
            content = item.get("content") or item.get("text") or ""
            combined_text = f"{title}\n\n{content}" if content else title
            incoming_source = (item.get("source") or "").strip() or None

            # --- Generate and normalize embedding ---
            new_emb = embed_text(combined_text)
            new_emb = self._flatten_embedding(new_emb)
            if not self._validate_embedding(new_emb, url, spider):
                return item

            spider.logger.debug(
                f"Embedding OK for {url} | len={len(new_emb)} | sample={new_emb[:5]}"
            )

            # --- Deduplication check ---
            now = datetime.now(timezone.utc)
            start, end = self._day_bounds(now)

            emb_vec = pgvector.Vector(new_emb)

            distance_expr = Article.embedding.cosine_distance(emb_vec)
            similarity_expr = (1 - distance_expr).label("sim")

            # Only consider potential duplicates from the same source; allow
            # similar stories from different sources to be stored separately.
            where_clauses = [
                Article.created_at >= start,
                Article.created_at < end,
                Article.embedding.is_not(None),
            ]
            if incoming_source is not None:
                where_clauses.append(Article.source == incoming_source)

            candidate = s.execute(
                select(Article, similarity_expr)
                .where(*where_clauses)
                .order_by(similarity_expr.desc())
                .limit(1)
            ).first()

            if candidate:
                existing, sim = candidate
                if sim is not None and sim >= 0.999999:
                    spider.logger.debug(f"Skipping identical article: {url}")
                    return item
                if sim is not None and sim > 0.9:
                    append_text = content or combined_text
                    existing.redundant_news = (existing.redundant_news or []) + [append_text]
                    s.add(existing)
                    s.commit()
                    spider.logger.info(f"Merged redundant article (sim={sim:.3f})")
                    return item

            # --- New article ---
            try:
                import asyncio
                summary = asyncio.run(generate_summary(content))
            except Exception as e:
                spider.logger.warning(f"Summary generation failed: {e}")
                summary = ""
            from utils.reliability import reliability_score

            # --- Trending score (per-article) ---
            try:
                published_at = item.get("published_at") or now
                source_for_trending = incoming_source or (item.get("source") or "")
                category_for_trending = item.get("category") or ""
                score_data = trending_engine.calculate_trending_score(
                    published_at=published_at,
                    source=source_for_trending,
                    category=category_for_trending,
                    similar_news=[],
                )
                trending_score = score_data["trending_score"]
            except Exception as e:
                spider.logger.warning(f"Trending score calculation failed: {e}")
                trending_score = 0.0

            data = {
                "title": title,
                "url": str(url),
                "summary": summary,
                "content": content or None,
                "author": item.get("author"),
                "published_at": item.get("published_at") or None,
                "source": item.get("source"),
                "embedding": new_emb,  # This should be the flattened list
                "reliability": reliability_score(
                    str(url), bool(item.get("author")), len(content or "")
                ),
                "trending_score": trending_score,
            }

            repo.create(s, data)
            spider.logger.info(f"Stored new article: {url}")

        except Exception as e:
            s.rollback()
            spider.logger.error(f"Error persisting article: {e}", exc_info=True)
        finally:
            s.close()
        return item

    # --- Helpers ---

    @staticmethod
    def _flatten_embedding(emb: Any) -> list[float] | None:
        """Force embedding to be a 1D list of floats."""
        if emb is None:
            return None
        arr = np.array(emb, dtype=float).flatten()
        return arr.tolist()

    @staticmethod
    def _validate_embedding(new_emb: Any, url: str, spider) -> bool:
        if new_emb is None:
            spider.logger.error(f"embed_text() returned None for {url}")
            return False
        if not isinstance(new_emb, list):
            spider.logger.error(f"Invalid embedding type {type(new_emb)} for {url}")
            return False
        if not all(isinstance(x, (int, float)) for x in new_emb):
            spider.logger.error(f"Non-numeric embedding values for {url}")
            return False
        return True

    @staticmethod
    def _day_bounds(dt: datetime) -> tuple[datetime, datetime]:
        start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return start, end
