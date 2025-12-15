from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.refresh_token_model import RefreshToken


def create(
    db: Session, *, user_id: int, token_hash: str, expires_at: datetime
) -> RefreshToken:
    item = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_by_token_hash(db: Session, token_hash: str) -> Optional[RefreshToken]:
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    return db.execute(stmt).scalar_one_or_none()


def revoke(db: Session, token: RefreshToken) -> None:
    from datetime import datetime, timezone

    if token.revoked_at is not None:
        return
    token.revoked_at = datetime.now(timezone.utc)
    db.add(token)
    db.commit()


def revoke_all_for_user(db: Session, user_id: int) -> None:
    from datetime import datetime, timezone

    stmt = select(RefreshToken).where(
        RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)
    )
    tokens: List[RefreshToken] = db.execute(stmt).scalars().all()
    if not tokens:
        return
    now = datetime.now(timezone.utc)
    for t in tokens:
        t.revoked_at = now
        db.add(t)
    db.commit()

