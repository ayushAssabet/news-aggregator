from sqlalchemy.orm import Session

from ..schemas import ArticleCreate
from ..services.article import article_service


def list_articles(db: Session, *, limit: int = 50, offset: int = 0):
    return article_service.list_articles(db, limit=limit, offset=offset)


def create_article(db: Session, payload: ArticleCreate):
    return article_service.create_article(db, payload)


def get_article(db: Session, article_id):
    return article_service.get_article(db, article_id)

