import uuid
import enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, Float, func, Enum
from pgvector.sqlalchemy import Vector

from app.database.base import Base


class ArticleCategory(enum.Enum):
    MUKHYA_SAMACHAR = "MUKHYA_SAMACHAR"
    RAJNITI = "RAJNITI"
    ARTH = "ARTH"
    KHELKUD = "KHELKUD"
    SAMAJ = "SAMAJ"
    SHIKSHA = "SHIKSHA"
    PRAVIDHI = "PRAVIDHI"
    MANORANJAN = "MANORANJAN"
    JALAVAYU = "JALAVAYU"
    APRADH = "APRADH"
    ANTARRASHTRIYA = "ANTARRASHTRIYA"
    PARYATAN = "PARYATAN"
    VICHAR = "VICHAR"


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(512))
    url: Mapped[str] = mapped_column(String(1024), unique=True)
    thumbnail: Mapped[str | None] = mapped_column(String(1024))
    summary: Mapped[str | None] = mapped_column(Text())
    content: Mapped[str | None] = mapped_column(Text())
    author: Mapped[str | None] = mapped_column(String(255))
    published_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    reliability: Mapped[float] = mapped_column(Float, default=0.0)
    trending_score: Mapped[float] = mapped_column(
        "trending_score", Float, default=0.0
    )
    category: Mapped[ArticleCategory] = mapped_column(
        Enum(ArticleCategory, name="article_category"), default=ArticleCategory.MUKHYA_SAMACHAR, nullable=False
    )
    redundant_news: Mapped[list[str] | None] = mapped_column(ARRAY(Text()))
    source: Mapped[str | None] = mapped_column(String(255))
    embedding: Mapped[list[float] | None] = mapped_column(Vector(3072))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
