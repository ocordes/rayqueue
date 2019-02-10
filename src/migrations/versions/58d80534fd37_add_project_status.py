"""add project status

Revision ID: 58d80534fd37
Revises: 99e0a1b981e8
Create Date: 2019-02-10 18:45:21.044011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '58d80534fd37'
down_revision = '99e0a1b981e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('status', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project', 'status')
    # ### end Alembic commands ###
