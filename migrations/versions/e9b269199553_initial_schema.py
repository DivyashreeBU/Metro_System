"""Initial schema

Revision ID: e9b269199553
Revises: 
Create Date: 2025-09-10 16:24:57.059577
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e9b269199553'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # STATION table updates
    with op.batch_alter_table('station', schema=None) as batch_op:
        batch_op.add_column(sa.Column('line_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_interchange', sa.Boolean(), nullable=True))
        batch_op.create_foreign_key(
            'fk_station_line_id',  # ✅ named foreign key
            'metro_line',
            ['line_id'],
            ['id']
        )
        batch_op.drop_column('zone')

    # TICKET table updates
    with op.batch_alter_table('ticket', schema=None) as batch_op:
        batch_op.alter_column('passenger_name', existing_type=sa.VARCHAR(length=100), nullable=False)
        batch_op.alter_column('phone', existing_type=sa.VARCHAR(length=20), nullable=False)
        batch_op.alter_column('train_id', existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column('from_station', existing_type=sa.VARCHAR(length=100), nullable=False)
        batch_op.alter_column('to_station', existing_type=sa.VARCHAR(length=100), nullable=False)
        batch_op.alter_column('fare', existing_type=sa.FLOAT(), nullable=False)
        batch_op.alter_column('created_at', existing_type=sa.DATETIME(), nullable=False)

    # USER table updates
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_user_email', ['email'])  # ✅ named unique constraint
        batch_op.drop_column('full_name')

def downgrade():
    # USER table rollback
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('full_name', sa.VARCHAR(length=100), nullable=True))
        batch_op.drop_constraint('uq_user_email', type_='unique')  # ✅ named for rollback

    # TICKET table rollback
    with op.batch_alter_table('ticket', schema=None) as batch_op:
        batch_op.alter_column('created_at', existing_type=sa.DATETIME(), nullable=True)
        batch_op.alter_column('fare', existing_type=sa.FLOAT(), nullable=True)
        batch_op.alter_column('to_station', existing_type=sa.VARCHAR(length=100), nullable=True)
        batch_op.alter_column('from_station', existing_type=sa.VARCHAR(length=100), nullable=True)
        batch_op.alter_column('train_id', existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column('phone', existing_type=sa.VARCHAR(length=20), nullable=True)
        batch_op.alter_column('passenger_name', existing_type=sa.VARCHAR(length=100), nullable=True)

    # STATION table rollback
    with op.batch_alter_table('station', schema=None) as batch_op:
        batch_op.add_column(sa.Column('zone', sa.VARCHAR(length=10), nullable=True))
        batch_op.drop_constraint('fk_station_line_id', type_='foreignkey')  # ✅ named for rollback
        batch_op.drop_column('is_interchange')
        batch_op.drop_column('line_id')