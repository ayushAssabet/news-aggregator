from sqlalchemy.orm import Session
from typing import Optional, List

from ...schemas import ArticleCreate
from ...models import Article
from utils.reliability import reliability_score
from ...repositories import article_repository as repo


def create_article(db: Session, payload: ArticleCreate) -> Article:
    # Quick exact URL dedupe for API-driven creation
    exists = repo.get_by_url(db, str(payload.url))
    if exists:
        return exists

    data = {
        "title": payload.title,
        "url": str(payload.url),
        "thumbnail": str(payload.thumbnail) if payload.thumbnail else None,
        "summary": payload.summary,
        "content": payload.content,
        "author": payload.author,
        "published_at": payload.published_at,
        "source": payload.source,
        "embedding": payload.embedding,
        "reliability": reliability_score(payload.model_dump()),
    }
    created = repo.create(db, data)
    return created


def list_articles(db: Session, limit: int = 50, offset: int = 0):
    return repo.list_articles(db, limit=limit, offset=offset)


def get_article(db: Session, article_id):
    return repo.get_by_id(db, article_id)
