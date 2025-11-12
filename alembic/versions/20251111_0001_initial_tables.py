"""Initial tables: articles, article_category enum, pgvector extension

Revision ID: 20251111_0001
Revises: 
Create Date: 2025-11-11
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql
import pgvector.sqlalchemy as pgv

revision: str = "20251111_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension (no-op if already installed)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Enum for article category (will be created implicitly with the table)
    article_category_enum = sa.Enum(
        "MUKHYA_SAMACHAR",
        "RAJNITI",
        "ARTH",
        "KHELKUD",
        "SAMAJ",
        "SHIKSHA",
        "PRAVIDHI",
        "MANORANJAN",
        "JALAVAYU",
        "APRADH",
        "ANTARRASHTRIYA",
        "PARYATAN",
        "VICHAR",
        name="article_category",
    )

    op.create_table(
        "articles",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("url", sa.String(1024), nullable=False, unique=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("author", sa.String(255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reliability", sa.Float, nullable=False, server_default=sa.text("0")),
        sa.Column("weight", sa.Float, nullable=False, server_default=sa.text("0")),
        sa.Column("category", article_category_enum, nullable=False, server_default=sa.text("'MUKHYA_SAMACHAR'")),
        sa.Column("redundant_news", psql.ARRAY(sa.Text()), nullable=True),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("embedding", pgv.Vector(3072), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("articles")
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS article_category")
    # Optionally drop pgvector extension
    op.execute("DROP EXTENSION IF EXISTS vector")
