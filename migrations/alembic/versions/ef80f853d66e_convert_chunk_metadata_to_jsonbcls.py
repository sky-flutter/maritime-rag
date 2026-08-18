"""convert chunk_metadata to jsonbcls

Revision ID: ef80f853d66e
Revises: 41ce00188a26
Create Date: 2026-08-18 15:27:15.361251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef80f853d66e'
down_revision: Union[str, Sequence[str], None] = '41ce00188a26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
