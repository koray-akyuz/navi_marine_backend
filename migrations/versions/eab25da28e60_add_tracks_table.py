"""add_tracks_table

Revision ID: eab25da28e60
Revises: 067df223c118
Create Date: 2026-03-16 17:17:44.715268

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = 'eab25da28e60'
down_revision: Union[str, Sequence[str], None] = '067df223c118'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('tracks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('geom', geoalchemy2.types.Geometry(geometry_type='LINESTRING', srid=4326, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False),
        sa.Column('points_json', sa.JSON(), nullable=False),
        sa.Column('distance', sa.Float(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tracks_id'), 'tracks', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_tracks_id'), table_name='tracks')
    op.drop_table('tracks')
