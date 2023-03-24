"""add post images tables

Revision ID: 1026a4342099
Revises: 6a6a7d1aa836
Create Date: 2023-03-02 21:29:38.112986

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1026a4342099'
down_revision = '6a6a7d1aa836'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('post_images',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('post_id', sa.String(), nullable=False),
    sa.Column('image', sa.Text(), nullable=True),
    sa.Column('created_by', sa.String(), nullable=False),
    sa.Column('created_date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['enterprise.users.username'], ),
    sa.ForeignKeyConstraint(['post_id'], ['post.post.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='post'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post_images', schema='post')
    # ### end Alembic commands ###