"""Added bez nazvu columns

Revision ID: 922989acece5
Revises: 61c8e5f7839a
Create Date: 2020-09-23 11:27:43.599529

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '922989acece5'
down_revision = '61c8e5f7839a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('provozovny', sa.Column('bez_nazvu_el', sa.Float(), nullable=True))
    op.add_column('provozovny', sa.Column('bez_nazvu_tep', sa.Float(), nullable=True))
    op.add_column('subjekty', sa.Column('bez_nazvu_el', sa.Float(), nullable=True))
    op.add_column('subjekty', sa.Column('bez_nazvu_tep', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subjekty', 'bez_nazvu_tep')
    op.drop_column('subjekty', 'bez_nazvu_el')
    op.drop_column('provozovny', 'bez_nazvu_tep')
    op.drop_column('provozovny', 'bez_nazvu_el')
    # ### end Alembic commands ###