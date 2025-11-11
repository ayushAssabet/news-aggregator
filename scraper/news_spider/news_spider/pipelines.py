from sqlalchemy.orm import Session
from twisted.internet.threads import deferToThread
from api.app.database.db import SessionLocal, engine
from api.app.database.schemas import ArticleCreate
from api.app.services import article_service
from api.app.config.settings import settings
import os


class StoreArticlePipeline:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(os.getenv("DATABASE_URL"))

    def open_spider(self, spider):
        # In production, rely on Alembic migrations to create tables.
        # Optionally allow auto-create for dev via AUTO_CREATE_TABLES=true.
        if settings.enable_auto_create_tables:
            try:
                from api.app.database.models import Base  # local import to avoid heavy import on module load
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
            payload = ArticleCreate(
                title=item.get("title"),
                url=item.get("url"),
                summary=(item.get("summary") or None),
                content=item.get("content") or item.get("text"),
                author=item.get("author"),
                published_at=item.get("published_at") or None,
            )
            article_service.create_article(s, payload)
        except Exception as e:
            s.rollback()
            spider.logger.error(f"DB error: {e}")
        finally:
            s.close()
        return item


