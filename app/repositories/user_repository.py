from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..models import User


def get_by_email(db: Session, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    return db.execute(stmt).scalar_one_or_none()


def create(db: Session, data: dict) -> User:
    user = User(**data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def soft_delete(db: Session, user_id: int) -> None:
    user = db.get(User, user_id)
    if not user:
        return
    from datetime import datetime, timezone

    user.deleted_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
