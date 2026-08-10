"""create chunks table

Revision ID: 847a51bc009b
Revises: 
Create Date: 2026-08-07 15:22:02.867408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from pgvector.sqlalchemy import Vector

EMBEDDING_DIM = 1536

# revision identifiers, used by Alembic.
revision: str = '847a51bc009b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "report_chunks",
        sa.Column("chunk_id", sa.String(), primary_key=True),
        sa.Column("report_id", sa.String(), nullable=False, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=False),
        sa.Column("embedding_model", sa.String(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )

    op.execute(
        "CREATE INDEX report_chunks_embedding_idx "
        "ON report_chunks USING ivfflat (embedding vector_cosine_ops) "
        "WITH (lists = 100)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("report_chunks_embedding_idx", table="report_chunks")
    op.drop_table("report_chunks")

