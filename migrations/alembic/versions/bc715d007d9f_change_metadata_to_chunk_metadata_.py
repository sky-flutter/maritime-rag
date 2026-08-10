"""change_metadata_to_chunk_metadata_report_chunk_table

Revision ID: bc715d007d9f
Revises: 847a51bc009b
Create Date: 2026-08-07 15:36:02.805700

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc715d007d9f'
down_revision: Union[str, Sequence[str], None] = '847a51bc009b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "report_chunks",
        "metadata",
        new_column_name="chunk_metadata",
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "report_chunks",
        "chunk_metadata",
        new_column_name="metadata",
    )
