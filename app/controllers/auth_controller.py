from sqlalchemy.orm import Session

from ..schemas import UserCreate, LoginRequest
from ..services.auth import auth_service
from ..models import User


def register_user(db: Session, payload: UserCreate) -> User:
    return auth_service.register_user(db, email=payload.email, password=payload.password, full_name=payload.full_name)


def login(db: Session, payload: LoginRequest) -> dict | None:
    user = auth_service.authenticate_user(db, payload.email, payload.password)
    if not user:
        return None
    access = auth_service.create_access_token(str(user.id))
    refresh = auth_service.create_refresh_token(str(user.id))
    return {"access_token": access, "refresh_token": refresh}
