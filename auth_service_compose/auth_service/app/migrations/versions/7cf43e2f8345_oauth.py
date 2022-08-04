"""oauth

Revision ID: 7cf43e2f8345
Revises: ace74b8b0f27
Create Date: 2022-08-02 13:15:16.639834

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7cf43e2f8345'
down_revision = 'ace74b8b0f27'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('oauth',
    sa.Column('type', sa.Enum('google', name='oauthenum'), nullable=False),
    sa.Column('sub', sa.String(), nullable=False),
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('oauth')
    # ### end Alembic commands ###