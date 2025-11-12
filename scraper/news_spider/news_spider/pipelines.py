from app.services.summarize.summarize_service import generate_summary
from sqlalchemy.orm import Session
from sqlalchemy import select, literal , bind 
from twisted.internet.threads import deferToThread
from pgvector.sqlalchemy import Vector
from app.database.db import SessionLocal, engine
from app.repositories import article_repository as repo
from app.models import Article
from app.services.embedding.model_provider import embed_text
from app.config.settings import settings
import os


class StoreArticlePipeline:

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(os.getenv("DATABASE_URL"))

    def open_spider(self, spider):

        if settings.enable_auto_create_tables:
            try:
                from app.database.base import Base  # local import to avoid heavy import on module load
                Base.metadata.create_all(engine)
            except Exception as e:
                spider.logger.warning(f"Auto table creation skipped: {e}")
        self.Session = SessionLocal

    def process_item(self, item, spider):
        # Run potentially blocking summarization + DB write in a thread
        return deferToThread(self._persist_item, dict(item), spider)

    def _persist_item(self, item: dict, spider):
        s: Session = self.Session()
        try:
            # Quick URL dedupe
            url = item.get("url")
            if not url:
                return item
            exists = repo.get_by_url(s, str(url))
            if exists:
                return item

            title = item.get("title") or ""
            content = item.get("content") or item.get("text") or ""
            combined_text = title + ("\n\n" + content if content else "")
            new_emb = embed_text(combined_text)

            if new_emb is None:
                spider.logger.error(f"embed_text() returned None for {url}")
                return item

            if not isinstance(new_emb, (list, tuple)):
                spider.logger.error(f"embed_text() returned invalid type {type(new_emb)} for {url}: {new_emb}")
                return item

            if not all(isinstance(x, (int, float)) for x in new_emb):
                spider.logger.error(f"embed_text() produced non-numeric values for {url}")
                return item

            spider.logger.debug(f"Embedding length={len(new_emb)}, sample={new_emb[:5]}")

            # Candidates: today UTC with embeddings
            from datetime import datetime, timezone, timedelta

            now = datetime.now(timezone.utc)
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)

            vec_lit = literal(new_emb, type_=Vector(3072))
            distance_expr = Article.embedding.op('<=>')(bindparam("embedding_vec", new_emb, type_=Vector(3072)))
            similarity_expr = (1 - distance_expr).label('sim')

            candidate = s.execute(
                select(Article, similarity_expr)
                .where(
                    Article.created_at >= start,
                    Article.created_at < end,
                    Article.embedding.is_not(None),
                )
                .order_by(similarity_expr.desc())
                .limit(1)
            ).first()

            if candidate:
                existing, sim = candidate
                if sim is not None and sim >= 0.999999:
                    return item
                if sim is not None and sim > 0.9:
                    append_text = content or combined_text
                    existing.redundant_news = (existing.redundant_news or []) + [append_text]
                    s.add(existing)
                    s.commit()
                    return item

            data = {
                "title": title,
                "url": str(url),
                "summary": generate_summary(content),
                "content": content or None,
                "author": item.get("author"),
                "published_at": item.get("published_at") or None,
                "source": item.get("source"),
                "embedding": new_emb,
            }
            from utils.reliability import reliability_score

            data["reliability"] = reliability_score(
                str(url), bool(data.get("author")), len((content or ""))
            )
            repo.create(s, data)
        except Exception as e:
            s.rollback()
            spider.logger.error(f"DB error: {e}")
        finally:
            s.close()
        return item
