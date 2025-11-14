from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
import uuid


class ArticleCreate(BaseModel):
    title: str
    url: HttpUrl
    summary: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    source: Optional[str] = None
    embedding: Optional[list[float]] = None
    trending_score: float
    reliability: float


class ArticleRead(BaseModel):
    id: uuid.UUID
    title: str
    url: HttpUrl
    summary: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    reliability: float
    trending_score: float
    source: Optional[str] = None
    redundant_news: Optional[list[str]] = None

    class Config:
        from_attributes = True
