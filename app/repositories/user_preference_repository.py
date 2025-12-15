from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.user_preference_model import UserPreference
from ..models.article_model import ArticleCategory


DEFAULT_SELECTED_WEIGHT = 0.8
DEFAULT_UNSELECTED_WEIGHT = 0.2


def list_preferences_for_user(db: Session, user_id: int) -> List[UserPreference]:
    stmt = select(UserPreference).where(UserPreference.user_id == user_id)
    return db.execute(stmt).scalars().all()


def create_initial_preferences(
    db: Session, user_id: int, selected_categories: list[ArticleCategory]
) -> List[UserPreference]:
    preferences: list[UserPreference] = []
    for cat in ArticleCategory:
        weight = (
            DEFAULT_SELECTED_WEIGHT
            if cat in selected_categories
            else DEFAULT_UNSELECTED_WEIGHT
        )
        pref = UserPreference(user_id=user_id, category=cat, weight=weight)
        db.add(pref)
        preferences.append(pref)
    db.commit()
    for pref in preferences:
        db.refresh(pref)
    return preferences

