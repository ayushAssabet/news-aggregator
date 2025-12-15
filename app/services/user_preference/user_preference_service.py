from typing import List

from sqlalchemy.orm import Session

from ...models.article_model import ArticleCategory
from ...models.user_preference_model import UserPreference
from ...repositories import user_preference_repository as repo


def list_preferences(db: Session, user_id: int) -> List[UserPreference]:
    return repo.list_preferences_for_user(db, user_id)


def create_initial_preferences(
    db: Session, user_id: int, selected_categories: list[ArticleCategory]
) -> List[UserPreference]:
    existing = repo.list_preferences_for_user(db, user_id)
    if existing:
        return existing
    return repo.create_initial_preferences(db, user_id, selected_categories)


def list_available_categories() -> dict[str, str]:
    # Map of English category keys to Nepali translations
    category_translations = {
        "MUKHYA_SAMACHAR": "मुख्य समाचार",
        "RAJNITI": "राजनीति",
        "ARTH": "अर्थ",
        "KHELKUD": "खेलकुद",
        "SAMAJ": "समाज",
        "SHIKSHA": "शिक्षा",
        "PRAVIDHI": "प्रविधि",
        "MANORANJAN": "मनोरञ्जन",
        "JALAVAYU": "जलवायु",
        "APRADH": "अपराध",
        "ANTARRASHTRIYA": "अन्तर्राष्ट्रिय",
        "PARYATAN": "पर्यटन",
        "VICHAR": "विचार"
    }
    return category_translations
