"""add password column

Revision ID: 376d29e79a14
Revises: 4449d14ef219
Create Date: 2025-12-13 12:16:19.576284

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '376d29e79a14'
down_revision: Union[str, Sequence[str], None] = '4449d14ef219'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('password', sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'password')
    pass
