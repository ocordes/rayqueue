"""add a created attreibute to QueueElemet

Revision ID: 802488a70265
Revises: 1b7cac9bf066
Create Date: 2019-03-11 18:08:38.620137

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '802488a70265'
down_revision = '1b7cac9bf066'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('queue_element', sa.Column('created', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_queue_element_created'), 'queue_element', ['created'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_queue_element_created'), table_name='queue_element')
    op.drop_column('queue_element', 'created')
    # ### end Alembic commands ###
