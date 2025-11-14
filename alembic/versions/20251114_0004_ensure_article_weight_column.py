"""Ensure articles.weight column exists

Revision ID: 20251114_0004
Revises: 20251114_0003
Create Date: 2025-11-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa  # noqa: F401


revision: str = "20251114_0004"
down_revision: Union[str, None] = "20251114_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Some existing databases may have been created without the trending_score column.
    # Ensure it exists with a reasonable default.
    op.execute(
        "ALTER TABLE articles "
        "ADD COLUMN IF NOT EXISTS trending_score FLOAT DEFAULT 0;"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE articles "
        "DROP COLUMN IF EXISTS trending_score;"
    )
