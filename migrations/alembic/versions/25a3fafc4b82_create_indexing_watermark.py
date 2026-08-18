"""create_indexing_watermark

Revision ID: 25a3fafc4b82
Revises: ef80f853d66e
Create Date: 2026-08-18 17:22:07.167045

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "25a3fafc4b82"
down_revision: Union[str, Sequence[str], None] = "ef80f853d66e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
table_name = "indexing_watermark"


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        table_name,
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("last_processed_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table(table_name)
