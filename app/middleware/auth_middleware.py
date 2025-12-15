from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..repositories import user_repository as repo
from ..models import User
from ..services.auth import auth_service


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            try:
                payload = auth_service.decode_token(token)
                sub = payload.get("sub")
                if sub:
                    try:
                        request.state.user_id = int(sub)
                    except ValueError:
                        pass
            except Exception:
                # Silently ignore invalid tokens; routes can enforce auth via dependency
                pass
        response = await call_next(request)
        return response


def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user = repo.get_by_id(db, user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication")
    return user
