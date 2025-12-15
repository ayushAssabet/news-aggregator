from __future__ import annotations

from datetime import datetime
from typing import List
import uuid

from pydantic import BaseModel

from app.models.article_model import ArticleCategory


class UserPreferenceRead(BaseModel):
    id: uuid.UUID
    user_id: int
    category: ArticleCategory
    weight: float
    last_updated: datetime

    class Config:
        from_attributes = True


class UserPreferenceInitRequest(BaseModel):
    selected_categories: List[ArticleCategory]

