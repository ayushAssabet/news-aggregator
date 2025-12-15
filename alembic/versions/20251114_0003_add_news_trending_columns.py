"""Add trending and scoring columns to news table

Revision ID: 20251114_0003
Revises: 20251111_0002
Create Date: 2025-11-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20251114_0003"
down_revision: Union[str, None] = "20251111_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "articles",
        sa.Column("trending_score", sa.Float(), server_default="0")
    )
    op.add_column(
        "articles",
        sa.Column("coverage_count", sa.Integer(), server_default="1")
    )
    op.add_column(
        "articles",
        sa.Column("source_weight", sa.Float(), server_default="0.5")
    )
    op.add_column(
        "articles",
        sa.Column("last_score_update", sa.TIMESTAMP(timezone=False), nullable=True)
    )
    op.drop_column("articles" , "weight")


def downgrade() -> None:
    op.drop_column("articles", "trending_score")
    op.drop_column("articles", "coverage_count")
    op.drop_column("articles", "source_weight")
    op.drop_column("articles", "last_score_update")
    op.add_column(
        "articles",
        sa.Column("weight", sa.Float(), server_default="0.5")
    )