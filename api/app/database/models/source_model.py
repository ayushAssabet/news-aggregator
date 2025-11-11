from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from .base import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    domain: Mapped[str] = mapped_column(String(255), unique=True)
    articles = relationship("Article", back_populates="source")

