"""add error_code to image

Revision ID: 8035b2af0b71
Revises: 74d179845630
Create Date: 2019-04-06 13:57:33.610606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8035b2af0b71'
down_revision = '74d179845630'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('image', sa.Column('error_code', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('image', 'error_code')
    # ### end Alembic commands ###
