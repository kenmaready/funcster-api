"""empty message

Revision ID: 5e0399731093
Revises: 
Create Date: 2020-05-21 11:34:08.537882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e0399731093'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.add_column('snippet', sa.Column('coder_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'snippet', 'coders', ['coder_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'snippet', type_='foreignkey')
    op.drop_column('snippet', 'coder_id')
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(length=24), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='user_pkey'),
    sa.UniqueConstraint('username', name='user_username_key')
    )
    # ### end Alembic commands ###
