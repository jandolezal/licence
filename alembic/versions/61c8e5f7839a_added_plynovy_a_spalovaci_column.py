"""Added plynovy a spalovaci column

Revision ID: 61c8e5f7839a
Revises: 8e906b0ea6a7
Create Date: 2020-09-23 11:25:43.184065

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61c8e5f7839a'
down_revision = '8e906b0ea6a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('provozovny', sa.Column('plynovy_a_spalovaci_el', sa.Float(), nullable=True))
    op.add_column('provozovny', sa.Column('plynovy_a_spalovaci_tep', sa.Float(), nullable=True))
    op.add_column('subjekty', sa.Column('plynovy_a_spalovaci_el', sa.Float(), nullable=True))
    op.add_column('subjekty', sa.Column('plynovy_a_spalovaci_tep', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subjekty', 'plynovy_a_spalovaci_tep')
    op.drop_column('subjekty', 'plynovy_a_spalovaci_el')
    op.drop_column('provozovny', 'plynovy_a_spalovaci_tep')
    op.drop_column('provozovny', 'plynovy_a_spalovaci_el')
    # ### end Alembic commands ###