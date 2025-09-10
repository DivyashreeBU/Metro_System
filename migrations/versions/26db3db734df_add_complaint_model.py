"""Add Complaint model

Revision ID: 26db3db734df
Revises: a9cbca0f3ec0
Create Date: 2025-09-10 21:50:00.308860

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26db3db734df'
down_revision = 'a9cbca0f3ec0'
branch_labels = None
depends_on = None


from sqlalchemy import inspect

def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)
    if 'complaint' not in inspector.get_table_names():
        op.create_table(
            'complaint',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('email', sa.String(length=100), nullable=False),
            sa.Column('subject', sa.String(length=150), nullable=False),
            sa.Column('message', sa.Text(), nullable=False)
        )

def downgrade():
    op.drop_table('complaint')
    # ### end Alembic commands ###


