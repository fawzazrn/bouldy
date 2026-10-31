"""Add gym brands, locked grade scales and route kinds

Revision ID: a1c4e7b90d12
Revises: f85cf24f0130
Create Date: 2026-10-31 22:40:00.000000

Additive only: new tables, new nullable columns, and seed data for Batuu,
Boulder Story and Camp 5. Existing rows and the legacy routes.grade text are
left untouched.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.seed.catalogue import seed_catalogue


# revision identifiers, used by Alembic.
revision: str = 'a1c4e7b90d12'
down_revision: Union[str, Sequence[str], None] = 'f85cf24f0130'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'grade_scales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('kind', sa.String(length=30), nullable=False),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'grades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scale_id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=10), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('colour_hex', sa.String(length=7), nullable=True),
        sa.Column('v_range_label', sa.String(length=30), nullable=True),
        sa.Column('font_range_label', sa.String(length=30), nullable=True),
        sa.Column('description', sa.String(length=100), nullable=True),
        sa.Column('band', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['scale_id'], ['grade_scales.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('scale_id', 'label', name='uq_grades_scale_label'),
        sa.UniqueConstraint('scale_id', 'order', name='uq_grades_scale_order'),
    )
    op.create_table(
        'gym_brands',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('grade_scale_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['grade_scale_id'], ['grade_scales.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug'),
    )
    op.create_table(
        'brand_route_kinds',
        sa.Column('brand_id', sa.Integer(), nullable=False),
        sa.Column('route_kind', sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(['brand_id'], ['gym_brands.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('brand_id', 'route_kind'),
    )

    op.add_column('gyms', sa.Column('brand_id', sa.Integer(), nullable=True))
    op.add_column('gyms', sa.Column('address', sa.Text(), nullable=True))
    op.add_column('gyms', sa.Column('city', sa.String(length=100), nullable=True))
    op.add_column('gyms', sa.Column('state', sa.String(length=100), nullable=True))
    op.add_column('gyms', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('gyms', sa.Column('longitude', sa.Float(), nullable=True))
    op.add_column('gyms', sa.Column('phone', sa.String(length=50), nullable=True))
    op.add_column('gyms', sa.Column('opening_hours', sa.Text(), nullable=True))
    op.add_column(
        'gyms',
        sa.Column('is_active', sa.Boolean(), server_default=sa.true(), nullable=False),
    )
    op.create_foreign_key('fk_gyms_brand_id', 'gyms', 'gym_brands', ['brand_id'], ['id'])

    op.add_column('routes', sa.Column('grade_id', sa.Integer(), nullable=True))
    op.add_column('routes', sa.Column('route_kind', sa.String(length=30), nullable=True))
    op.create_foreign_key('fk_routes_grade_id', 'routes', 'grades', ['grade_id'], ['id'])

    seed_catalogue(op.get_bind())


def downgrade() -> None:
    """Downgrade schema.

    Gym rows created by the seed are NOT deleted, because sessions may already
    reference them. Their brand and address columns are dropped with the rest.
    """
    op.drop_constraint('fk_routes_grade_id', 'routes', type_='foreignkey')
    op.drop_column('routes', 'route_kind')
    op.drop_column('routes', 'grade_id')

    op.drop_constraint('fk_gyms_brand_id', 'gyms', type_='foreignkey')
    op.drop_column('gyms', 'is_active')
    op.drop_column('gyms', 'opening_hours')
    op.drop_column('gyms', 'phone')
    op.drop_column('gyms', 'longitude')
    op.drop_column('gyms', 'latitude')
    op.drop_column('gyms', 'state')
    op.drop_column('gyms', 'city')
    op.drop_column('gyms', 'address')
    op.drop_column('gyms', 'brand_id')

    op.drop_table('brand_route_kinds')
    op.drop_table('gym_brands')
    op.drop_table('grades')
    op.drop_table('grade_scales')
