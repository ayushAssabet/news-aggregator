from sqlalchemy.orm import Session
from twisted.internet.threads import deferToThread
from api.app.db import SessionLocal, engine
from api.app.models import Base
from api.app.schemas import ArticleCreate
from api.app.services import article_service
import os


class StoreArticlePipeline:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(os.getenv("DATABASE_URL"))

    def open_spider(self, spider):
        # Ensure tables exist (safe to call)
        Base.metadata.create_all(engine)
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
