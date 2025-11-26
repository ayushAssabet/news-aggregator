from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..schemas import UserPreferenceRead, UserPreferenceInitRequest
from ..controllers import user_preference_controller
from ..middleware.auth_middleware import require_user
from ..models import User, ArticleCategory


router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("/categories", response_model=list[ArticleCategory])
def list_available_categories():
    return user_preference_controller.list_available_categories()


@router.get("/", response_model=list[UserPreferenceRead])
def list_preferences(
    db: Session = Depends(get_db), current_user: User = Depends(require_user)
):
    return user_preference_controller.list_preferences(db, current_user)


@router.post("/initial", response_model=list[UserPreferenceRead])
def create_initial_preferences(
    payload: UserPreferenceInitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    try:
        return user_preference_controller.create_initial_preferences(
            db, current_user, payload.selected_categories
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
