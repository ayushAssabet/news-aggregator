from sqlalchemy.orm import Session

from ..models.article_model import ArticleCategory
from ..services.user_preference import user_preference_service
from ..models import User


def list_preferences(db: Session, user: User):
    return user_preference_service.list_preferences(db, user.id)


def create_initial_preferences(
    db: Session, user: User, selected_categories: list[ArticleCategory]
):
    return user_preference_service.create_initial_preferences(
        db, user.id, selected_categories
    )


def list_available_categories():
    return user_preference_service.list_available_categories()
