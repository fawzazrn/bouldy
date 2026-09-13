"""fix routestyle enum labels to match model values

Revision ID: f85cf24f0130
Revises: 957601bed621
Create Date: 2026-09-13 13:33:21.718214

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.models.enums import RouteStyle


# revision identifiers, used by Alembic.
revision: str = 'f85cf24f0130'
down_revision: Union[str, Sequence[str], None] = '957601bed621'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# The `routestyle` Postgres enum type was originally created using the Python
# enum member NAMES (e.g. "CRIMPS", "HEEL_HOOK") instead of the string VALUES
# the model actually sends via `values_callable` (e.g. "Crimps", "Heel Hook").
# This renames each label in place so existing usages of the type still work.
def upgrade() -> None:
    """Upgrade schema."""
    for style in RouteStyle:
        op.execute(
            f"ALTER TYPE routestyle RENAME VALUE '{style.name}' TO '{style.value}'"
        )


def downgrade() -> None:
    """Downgrade schema."""
    for style in RouteStyle:
        op.execute(
            f"ALTER TYPE routestyle RENAME VALUE '{style.value}' TO '{style.name}'"
        )
