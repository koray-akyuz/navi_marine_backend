"""add_weather_columns_to_fish_reports

Revision ID: a3f8c2d1e905
Revises: f9b11a23b067
Create Date: 2026-03-13 20:09:38.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f8c2d1e905'
down_revision: Union[str, Sequence[str], None] = 'f9b11a23b067'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """fish_reports tablosuna hava durumu kolonlarını ekle."""
    op.add_column('fish_reports', sa.Column('wind_speed',  sa.Float(),      nullable=True))
    op.add_column('fish_reports', sa.Column('wind_deg',    sa.Float(),      nullable=True))
    op.add_column('fish_reports', sa.Column('wind_name',   sa.String(50),   nullable=True))
    op.add_column('fish_reports', sa.Column('temperature', sa.Float(),      nullable=True))


def downgrade() -> None:
    """Hava durumu kolonlarını kaldır."""
    op.drop_column('fish_reports', 'temperature')
    op.drop_column('fish_reports', 'wind_name')
    op.drop_column('fish_reports', 'wind_deg')
    op.drop_column('fish_reports', 'wind_speed')
