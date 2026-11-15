"""Convert attempts.result to attempt_result_enum

Revision ID: c3e9a7d2f4b1
Revises: b2d5f8a1c3e7
Create Date: 2026-11-15 12:00:00.000000

0b8be4a22fee was meant to do this but was generated empty, so the column
stayed VARCHAR(20). Existing values are cast in place; any value outside
the enum will make the upgrade fail rather than be silently dropped.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c3e9a7d2f4b1'
down_revision: Union[str, Sequence[str], None] = 'b2d5f8a1c3e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


attempt_result_enum = postgresql.ENUM(
    'flash', 'zone', 'send', 'project', name='attempt_result_enum'
)


def upgrade() -> None:
    """Upgrade schema."""
    attempt_result_enum.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        'attempts',
        'result',
        existing_type=sa.String(length=20),
        type_=attempt_result_enum,
        existing_nullable=False,
        postgresql_using='result::attempt_result_enum',
        server_default='project',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'attempts',
        'result',
        existing_type=attempt_result_enum,
        type_=sa.String(length=20),
        existing_nullable=False,
        postgresql_using='result::text',
        server_default=None,
    )
    attempt_result_enum.drop(op.get_bind(), checkfirst=True)
