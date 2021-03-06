"""add width,height for files

Revision ID: 72324d818f1f
Revises: 3cc4163bc4c5
Create Date: 2019-04-18 10:36:48.316925

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72324d818f1f'
down_revision = '3cc4163bc4c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('file', sa.Column('im_height', sa.Integer(), nullable=True))
    op.add_column('file', sa.Column('im_width', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('file', 'im_width')
    op.drop_column('file', 'im_height')
    # ### end Alembic commands ###
