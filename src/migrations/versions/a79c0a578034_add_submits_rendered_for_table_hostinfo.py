"""add submits,rendered for table hostinfo

Revision ID: a79c0a578034
Revises: e58f689bc899
Create Date: 2019-05-04 13:51:06.705312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a79c0a578034'
down_revision = 'e58f689bc899'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('host_info', sa.Column('rendered', sa.Integer(), nullable=True))
    op.add_column('host_info', sa.Column('submits', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('host_info', 'submits')
    op.drop_column('host_info', 'rendered')
    # ### end Alembic commands ###
