"""add models 'UserRefreshToken' and 'UserWhiteIP'

Revision ID: 76e16adf33a6
Revises: 9df116391e3d
Create Date: 2022-12-24 11:49:55.723727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76e16adf33a6'
down_revision = '9df116391e3d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_refresh_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=False),
    sa.Column('refresh_token', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_refresh_token_id'), 'user_refresh_token', ['id'], unique=False)
    op.create_table('user_white_ip',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=False),
    sa.Column('white_ip', sa.String(length=30), nullable=False),
    sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_white_ip_id'), 'user_white_ip', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_white_ip_id'), table_name='user_white_ip')
    op.drop_table('user_white_ip')
    op.drop_index(op.f('ix_user_refresh_token_id'), table_name='user_refresh_token')
    op.drop_table('user_refresh_token')
    # ### end Alembic commands ###