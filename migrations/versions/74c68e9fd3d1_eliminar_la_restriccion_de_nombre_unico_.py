"""Eliminar la restriccion de nombre unico de tournament

Revision ID: 74c68e9fd3d1
Revises: b5437d7a0790
Create Date: 2019-01-21 01:05:59.717805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74c68e9fd3d1'
down_revision = 'b5437d7a0790'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_tournament_name', table_name='tournament')
    op.create_index(op.f('ix_tournament_name'), 'tournament', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tournament_name'), table_name='tournament')
    op.create_index('ix_tournament_name', 'tournament', ['name'], unique=1)
    # ### end Alembic commands ###
