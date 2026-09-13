"""add route name to routes (fix missing column)

Revision ID: 957601bed621
Revises: 0b8be4a22fee
Create Date: 2026-09-13 13:26:45.559327

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '957601bed621'
down_revision: Union[str, Sequence[str], None] = '0b8be4a22fee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'routes',
        sa.Column('route_name', sa.String(length=100), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('routes', 'route_name')
