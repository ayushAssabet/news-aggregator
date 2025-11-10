from sqlalchemy.orm import Session
from typing import Optional, List
from ..schemas import ArticleCreate
from .. import models
from utils.dedupe import fingerprint
from utils.reliability import reliability_score
from ..repositories import article_repository as repo


def create_article(db: Session, payload: ArticleCreate) -> models.Article:
    fp = fingerprint(payload.title, str(payload.url))
    exists = repo.get_by_fingerprint(db, fp)
    if exists:
        return exists
    data = {
        "title": payload.title,
        "url": str(payload.url),
        "summary": payload.summary,
        "content": payload.content,
        "author": payload.author,
        "published_at": payload.published_at,
        "fingerprint": fp,
        "reliability": reliability_score(
            str(payload.url), bool(payload.author), len(payload.content or "")
        ),
    }
    return repo.create(db, data)


def list_articles(db: Session, limit: int = 50, offset: int = 0):
    return repo.list_articles(db, limit=limit, offset=offset)


def get_article(db: Session, article_id):
    return repo.get_by_id(db, article_id)

