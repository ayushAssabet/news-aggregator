"""Add thumbnail column to articles table

Revision ID: 20251202_0005
Revises: 20251114_0004
Create Date: 2025-12-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20251202_0005"
down_revision: Union[str, None] = "20251114_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "articles",
        sa.Column("thumbnail", sa.String(1024), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("articles", "thumbnail")
