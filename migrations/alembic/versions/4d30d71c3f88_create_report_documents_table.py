"""create_report_documents_table

Revision ID: 4d30d71c3f88
Revises: bc715d007d9f
Create Date: 2026-08-17 18:34:08.861709

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB



# revision identifiers, used by Alembic.
revision: str = '4d30d71c3f88'
down_revision: Union[str, Sequence[str], None] = 'bc715d007d9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
table_name = "report_documents"

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        table_name,
        sa.Column("report_id", sa.String(), primary_key=True),
        sa.Column("data_source", sa.String(), nullable=True),
        sa.Column("customer_name", sa.String(), nullable=True),
        sa.Column("imo", sa.String(), nullable=True, index=True),
        sa.Column("report_type", sa.String(), nullable=True),
        sa.Column("datetime_gmt", sa.DateTime(timezone=True), nullable=True),
        sa.Column("report_json", JSONB(), nullable=False),
        sa.Column("record_hash", sa.String(), nullable=True),
        sa.Column("operation_type", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table(table_name)
