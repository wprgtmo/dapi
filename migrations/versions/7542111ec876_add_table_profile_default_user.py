"""add table profile default user

Revision ID: 7542111ec876
Revises: efadb466aad6
Create Date: 2023-06-29 14:05:10.333080

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7542111ec876'
down_revision = 'efadb466aad6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('profile_default_user',
    sa.Column('profile_id', sa.String(), nullable=False),
    sa.Column('sex', sa.String(length=1), nullable=True),
    sa.Column('birthdate', sa.Date(), nullable=True),
    sa.Column('alias', sa.String(length=30), nullable=True),
    sa.Column('job', sa.String(length=120), nullable=True),
    sa.Column('city_id', sa.Integer(), nullable=True, comment='City to which the player belongs'),
    sa.Column('photo', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('updated_by', sa.String(), nullable=False),
    sa.Column('updated_date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['city_id'], ['resources.city.id'], ),
    sa.ForeignKeyConstraint(['profile_id'], ['enterprise.profile_member.id'], ),
    sa.ForeignKeyConstraint(['updated_by'], ['enterprise.users.username'], ),
    sa.PrimaryKeyConstraint('profile_id'),
    schema='enterprise'
    )
    
def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('profile_default_user', schema='enterprise')
    