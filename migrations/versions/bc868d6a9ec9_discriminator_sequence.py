"""discriminator sequence

Revision ID: bc868d6a9ec9
Revises: 4862c64ff556
Create Date: 2025-02-18 14:56:22.796933

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc868d6a9ec9'
down_revision = '4862c64ff556'
branch_labels = None
depends_on = None


def upgrade():
    # current value needs to be manually adjusted!
    op.execute(sa.schema.CreateSequence(sa.Sequence('user_discriminator_seq', start=1)))


def downgrade():
    op.execute(sa.schema.DropSequence(sa.Sequence('user_discriminator_seq', start=1)))