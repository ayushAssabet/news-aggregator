from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ...config.settings import settings
from ...repositories import user_repository as repo
from ...models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _create_token(subject: str, *, expires_minutes: int, token_type: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
    now = datetime.now(timezone.utc)
    to_encode: Dict[str, Any] = {
        "sub": subject,
        "exp": now + timedelta(minutes=expires_minutes),
        "iat": now,
        "iss": settings.jwt_issuer,
        "type": token_type,
    }
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, *, expires_minutes: Optional[int] = None, extra_claims: Optional[Dict[str, Any]] = None) -> str:
    return _create_token(
        subject,
        expires_minutes=expires_minutes or settings.jwt_access_token_expires_minutes,
        token_type="access",
        extra_claims=extra_claims,
    )


def create_refresh_token(subject: str, *, expires_minutes: Optional[int] = None) -> str:
    return _create_token(
        subject,
        expires_minutes=expires_minutes or settings.jwt_refresh_token_expires_minutes,
        token_type="refresh",
    )


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        issuer=settings.jwt_issuer,
    )


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = repo.get_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if user.deleted_at is not None:
        return None
    return user


def register_user(db: Session, *, email: str, password: str, full_name: Optional[str] = None) -> User:
    existing = repo.get_by_email(db, email)
    if existing:
        raise ValueError("User with this email already exists")
    hashed = get_password_hash(password)
    return repo.create(db, {"email": email, "full_name": full_name, "hashed_password": hashed})


def get_user_from_token(db: Session, token: str) -> Optional[User]:
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            return None
        try:
            user_id = int(sub)
        except ValueError:
            return None
        return repo.get_by_id(db, user_id)
    except JWTError:
        return None


def exchange_refresh_token_for_pair(refresh_token: str) -> Optional[Dict[str, str]]:
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            return None
        sub = payload.get("sub")
        if not sub:
            return None
        access = create_access_token(sub)
        new_refresh = create_refresh_token(sub)
        return {"access_token": access, "refresh_token": new_refresh}
    except JWTError:
        return None
