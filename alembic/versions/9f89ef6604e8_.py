"""empty message

Revision ID: 9f89ef6604e8
Revises: 79926f99d4b9
Create Date: 2021-09-30 13:32:26.650716

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f89ef6604e8'
down_revision = '79926f99d4b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('glass_manufacture_price_glass_id_fkey', 'glass_manufacture_price', type_='foreignkey')
    op.drop_constraint('glass_manufacture_price_manufacture_id_fkey', 'glass_manufacture_price', type_='foreignkey')
    op.create_foreign_key(None, 'glass_manufacture_price', 'glass_type', ['glass_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'glass_manufacture_price', 'glass_manufacture', ['manufacture_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'glass_manufacture_price', type_='foreignkey')
    op.drop_constraint(None, 'glass_manufacture_price', type_='foreignkey')
    op.create_foreign_key('glass_manufacture_price_manufacture_id_fkey', 'glass_manufacture_price', 'glass_manufacture', ['manufacture_id'], ['id'])
    op.create_foreign_key('glass_manufacture_price_glass_id_fkey', 'glass_manufacture_price', 'glass_type', ['glass_id'], ['id'])
    # ### end Alembic commands ###