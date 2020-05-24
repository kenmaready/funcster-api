"""empty message

Revision ID: 841db7588f67
Revises: b49a929484f7
Create Date: 2020-05-24 09:28:57.500250

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '841db7588f67'
down_revision = 'b49a929484f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('snippet', sa.Column('comments', sa.String(), nullable=True))
    op.add_column('snippet', sa.Column('needs_review', sa.Boolean(), nullable=True))
    op.drop_column('snippet', 'code_type')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('snippet', sa.Column('code_type', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('snippet', 'needs_review')
    op.drop_column('snippet', 'comments')
    # ### end Alembic commands ###
