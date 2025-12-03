"""Merge all heads

Revision ID: 24fe1e3200fe
Revises: 116f080fc450, fabf6c284d26
Create Date: 2025-12-03 04:29:49.193061

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24fe1e3200fe'
down_revision = ('116f080fc450', 'fabf6c284d26')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
