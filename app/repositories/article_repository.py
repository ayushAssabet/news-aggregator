from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models import Article


def get_by_fingerprint(db: Session, fp: str) -> Optional[Article]:
    return db.execute(
        select(Article).where(Article.fingerprint == fp)
    ).scalar_one_or_none()


def create(db: Session, data: dict) -> Article:
    item = Article(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_articles(db: Session, limit: int = 50, offset: int = 0) -> List[Article]:
    stmt = (
        select(Article)
        .order_by(Article.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.execute(stmt).scalars().all()


def get_by_id(db: Session, article_id):
    return db.get(Article, article_id)
