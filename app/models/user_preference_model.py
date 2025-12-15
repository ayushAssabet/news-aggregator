import uuid
import enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Float, Enum, ForeignKey, DateTime, func

from app.database.base import Base
from app.models.article_model import ArticleCategory


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    category: Mapped[ArticleCategory] = mapped_column(
        Enum(ArticleCategory, name="user_pref_category"), nullable=False
    )

    weight: Mapped[float] = mapped_column(Float, default=0.5)  # 0–1 score

    last_updated: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
