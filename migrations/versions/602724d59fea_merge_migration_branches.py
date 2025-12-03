"""Merge migration branches

Revision ID: 602724d59fea
Revises: 5b8db782b72f, 8730b01a3e26, 8ed50aabb712
Create Date: 2025-11-18 17:31:38.828489

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '602724d59fea'
down_revision = ('5b8db782b72f', '8730b01a3e26', '8ed50aabb712')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
