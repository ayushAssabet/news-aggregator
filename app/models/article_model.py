import uuid
import enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, Float, ForeignKey, UniqueConstraint, func, Enum

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
    summary: Mapped[str | None] = mapped_column(Text())
    content: Mapped[str | None] = mapped_column(Text())
    author: Mapped[str | None] = mapped_column(String(255))
    published_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    reliability: Mapped[float] = mapped_column(Float, default=0.0)
    weight: Mapped[float] = mapped_column(Float, default=0.0)
    fingerprint: Mapped[str] = mapped_column(String(64), index=True)
    category: Mapped[ArticleCategory] = mapped_column(
        Enum(ArticleCategory, name="article_category"), default=ArticleCategory.MUKHYA_SAMACHAR, nullable=False
    )
    redundant_news: Mapped[str | None] = mapped_column(Text())
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    source = relationship("Source", back_populates="articles")

    __table_args__ = (UniqueConstraint("fingerprint", name="uq_article_fingerprint"),)
