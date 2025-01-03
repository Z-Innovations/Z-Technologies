"""Added credit card

Revision ID: 4f8edc7e024c
Revises: 
Create Date: 2024-12-30 13:11:17.226848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f8edc7e024c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creditcard_number', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('creditcard_valid_till', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('creditcard_3_digits', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('creditcard_3_digits')
        batch_op.drop_column('creditcard_valid_till')
        batch_op.drop_column('creditcard_number')

    # ### end Alembic commands ###
