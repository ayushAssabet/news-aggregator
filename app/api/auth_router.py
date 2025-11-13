from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..schemas import UserCreate, UserRead, LoginRequest, TokenPair, RefreshRequest
from ..controllers import auth_controller
from ..middleware.auth_middleware import require_user
from ..models import User


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        user = auth_controller.register_user(db, payload)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    pair = auth_controller.login(db, payload)
    if not pair:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return pair


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest):
    from ..services.auth import auth_service

    pair = auth_service.exchange_refresh_token_for_pair(payload.refresh_token)
    if not pair:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return pair


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(require_user)):
    return current_user
