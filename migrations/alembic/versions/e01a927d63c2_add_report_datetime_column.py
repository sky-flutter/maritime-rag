"""add_report_datetime_column

Revision ID: e01a927d63c2
Revises: 4d30d71c3f88
Create Date: 2026-08-18 15:16:55.786910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e01a927d63c2"
down_revision: Union[str, Sequence[str], None] = "4d30d71c3f88"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "report_chunks",
        sa.Column("report_datetime_gmt", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_report_chunks_datetime_gmt",
        "report_chunks",
        ["report_datetime_gmt"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_report_chunks_datetime_gmt", table_name="report_chunks")
    op.drop_column("report_chunks", "report_datetime_gmt")
