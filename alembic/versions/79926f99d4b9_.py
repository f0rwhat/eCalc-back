"""empty message

Revision ID: 79926f99d4b9
Revises: 4fe6bbf934e4
Create Date: 2021-09-16 17:05:23.566608

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79926f99d4b9'
down_revision = '4fe6bbf934e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('delivery_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_delivery_type_id'), 'delivery_type', ['id'], unique=False)
    op.create_table('elevator_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('priceMultiplier', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_elevator_type_id'), 'elevator_type', ['id'], unique=False)
    op.create_table('glass_drawing',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('discount', sa.Float(), nullable=True),
    sa.Column('markup', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_glass_drawing_id'), 'glass_drawing', ['id'], unique=False)
    op.create_table('glass_manufacture',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_glass_manufacture_id'), 'glass_manufacture', ['id'], unique=False)
    op.create_table('glass_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('discount', sa.Float(), nullable=True),
    sa.Column('markup', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_glass_type_id'), 'glass_type', ['id'], unique=False)
    op.create_table('package_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_package_type_id'), 'package_type', ['id'], unique=False)
    op.create_table('product_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_type_id'), 'product_type', ['id'], unique=False)
    op.create_table('util_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('info', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_util_info_id'), 'util_info', ['id'], unique=False)
    op.create_table('component',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['type_id'], ['product_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_component_id'), 'component', ['id'], unique=False)
    op.create_table('glass_manufacture_price',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('glass_id', sa.Integer(), nullable=True),
    sa.Column('manufacture_id', sa.Integer(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['glass_id'], ['glass_type.id'], ),
    sa.ForeignKeyConstraint(['manufacture_id'], ['glass_manufacture.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_glass_manufacture_price_id'), 'glass_manufacture_price', ['id'], unique=False)
    op.create_table('product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['type_id'], ['product_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_id'), 'product', ['id'], unique=False)
    op.create_table('product_composition',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('component_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['component_id'], ['component.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_composition_id'), 'product_composition', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_product_composition_id'), table_name='product_composition')
    op.drop_table('product_composition')
    op.drop_index(op.f('ix_product_id'), table_name='product')
    op.drop_table('product')
    op.drop_index(op.f('ix_glass_manufacture_price_id'), table_name='glass_manufacture_price')
    op.drop_table('glass_manufacture_price')
    op.drop_index(op.f('ix_component_id'), table_name='component')
    op.drop_table('component')
    op.drop_index(op.f('ix_util_info_id'), table_name='util_info')
    op.drop_table('util_info')
    op.drop_index(op.f('ix_product_type_id'), table_name='product_type')
    op.drop_table('product_type')
    op.drop_index(op.f('ix_package_type_id'), table_name='package_type')
    op.drop_table('package_type')
    op.drop_index(op.f('ix_glass_type_id'), table_name='glass_type')
    op.drop_table('glass_type')
    op.drop_index(op.f('ix_glass_manufacture_id'), table_name='glass_manufacture')
    op.drop_table('glass_manufacture')
    op.drop_index(op.f('ix_glass_drawing_id'), table_name='glass_drawing')
    op.drop_table('glass_drawing')
    op.drop_index(op.f('ix_elevator_type_id'), table_name='elevator_type')
    op.drop_table('elevator_type')
    op.drop_index(op.f('ix_delivery_type_id'), table_name='delivery_type')
    op.drop_table('delivery_type')
    # ### end Alembic commands ###
