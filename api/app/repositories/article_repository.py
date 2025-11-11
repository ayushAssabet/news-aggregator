from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import models


def get_by_fingerprint(db: Session, fp: str) -> Optional[models.Article]:
    return db.execute(
        select(models.Article).where(models.Article.fingerprint == fp)
    ).scalar_one_or_none()


def create(db: Session, data: dict) -> models.Article:
    item = models.Article(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_articles(db: Session, limit: int = 50, offset: int = 0) -> List[models.Article]:
    stmt = (
        select(models.Article)
        .order_by(models.Article.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.execute(stmt).scalars().all()


def get_by_id(db: Session, article_id):
    return db.get(models.Article, article_id)
