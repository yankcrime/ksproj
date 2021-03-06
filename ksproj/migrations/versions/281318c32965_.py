"""empty message

Revision ID: 281318c32965
Revises: 
Create Date: 2018-03-07 15:55:19.286499

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '281318c32965'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invitations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project', sa.String(length=60), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('role', sa.String(length=60), nullable=False),
    sa.Column('token', sa.String(length=60), nullable=False),
    sa.Column('invited_by', sa.String(length=60), nullable=False),
    sa.Column('invited_on', sa.DateTime(), nullable=False),
    sa.Column('accepted_by', sa.String(length=60), nullable=True),
    sa.Column('accepted_on', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project', 'email', name='uix_1')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('invitations')
    # ### end Alembic commands ###
