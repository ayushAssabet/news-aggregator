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


class ArticleRead(BaseModel):
    id: uuid.UUID
    title: str
    url: HttpUrl
    summary: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    reliability: float
    weight: float
    fingerprint: str

    class Config:
        from_attributes = True
