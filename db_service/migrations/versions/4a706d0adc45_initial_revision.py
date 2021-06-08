"""initial revision

Revision ID: 4a706d0adc45
Revises: 
Create Date: 2021-06-14 14:50:36.345866

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '4a706d0adc45'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('request_state',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )
    op.create_table('request_type',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )
    op.create_table('request',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('type_id', sa.Integer(), nullable=True),
                    sa.Column('state_id', sa.Integer(), nullable=True),
                    sa.Column('cbsd_id', sa.String(), nullable=False),
                    sa.Column('payload', sa.JSON(), nullable=True),
                    sa.ForeignKeyConstraint(['state_id'], ['request_state.id'], ),
                    sa.ForeignKeyConstraint(['type_id'], ['request_type.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('response',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('request_id', sa.Integer(), nullable=True),
                    sa.Column('response_code', sa.Integer(), nullable=False),
                    sa.Column('payload', sa.JSON(), nullable=True),
                    sa.ForeignKeyConstraint(['request_id'], ['request.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('response')
    op.drop_table('request')
    op.drop_table('request_type')
    op.drop_table('request_state')
    # ### end Alembic commands ###
