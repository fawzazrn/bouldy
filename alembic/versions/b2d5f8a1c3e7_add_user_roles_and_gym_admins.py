"""Add user roles and gym admin links

Revision ID: b2d5f8a1c3e7
Revises: a1c4e7b90d12
Create Date: 2026-10-31 23:10:00.000000

Every existing user becomes role 'user'. Nobody is promoted here: the first
super admin is created by running app.scripts.bootstrap_super_admin.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2d5f8a1c3e7'
down_revision: Union[str, Sequence[str], None] = 'a1c4e7b90d12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('role', sa.String(length=20), server_default='user', nullable=False),
    )
    op.create_table(
        'user_gym_admins',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('gym_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['gym_id'], ['gyms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'gym_id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_gym_admins')
    op.drop_column('users', 'role')
