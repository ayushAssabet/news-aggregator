"""Add user preferences and refresh tokens tables

Revision ID: 20251114_0004
Revises: 20251114_0003
Create Date: 2025-11-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql


revision: str = "20251114_0004"
down_revision: Union[str, None] = "20251114_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enum for user preference category (mirrors article_category)
    user_pref_category_enum = sa.Enum(
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
        name="user_pref_category",
    )

    op.create_table(
        "user_preferences",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("category", user_pref_category_enum, nullable=False),
        sa.Column(
            "weight",
            sa.Float(),
            nullable=False,
            server_default=sa.text("0.5"),
        ),
        sa.Column(
            "last_updated",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("refresh_tokens")
    op.drop_table("user_preferences")
    op.execute("DROP TYPE IF EXISTS user_pref_category")

