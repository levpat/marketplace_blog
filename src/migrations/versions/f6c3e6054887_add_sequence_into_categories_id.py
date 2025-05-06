"""Add sequence into categories_id

Revision ID: f6c3e6054887
Revises: 664f3728e29c
Create Date: 2025-05-01 17:55:16.677669

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6c3e6054887'
down_revision: Union[str, None] = '664f3728e29c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.execute("ALTER SEQUENCE categories_id_seq RESTART WITH 1")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")