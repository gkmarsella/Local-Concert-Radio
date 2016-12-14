"""empty message

Revision ID: aa803f71b271
Revises: 
Create Date: 2016-12-14 14:53:57.649836

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa803f71b271'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_name', sa.Text(), nullable=True),
    sa.Column('user_email', sa.Text(), nullable=True),
    sa.Column('disliked_genres', sa.Text(), nullable=True),
    sa.Column('disliked_artists', sa.Text(), nullable=True),
    sa.Column('interested_events', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    # ### end Alembic commands ###