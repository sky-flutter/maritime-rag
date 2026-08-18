"""convert chunk_metadata to jsonb

Revision ID: 41ce00188a26
Revises: e01a927d63c2
Create Date: 2026-08-18 15:26:24.746474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "41ce00188a26"
down_revision: Union[str, Sequence[str], None] = "e01a927d63c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "report_chunks",
        "chunk_metadata",
        type_=postgresql.JSONB(),
        postgresql_using="chunk_metadata::jsonb",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "report_chunks",
        "chunk_metadata",
        type_=postgresql.JSON(),
        postgresql_using="chunk_metadata::json",
    )
