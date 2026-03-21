"""cascade delete interactions when item is deleted

Revision ID: a1b2c3d4e5f6
Revises: 6decf5361049
Create Date: 2025-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '6decf5361049'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the old FK without cascade
    op.drop_constraint(
        'interactions_item_id_fkey',
        'interactions',
        type_='foreignkey',
    )
    # Re-create with ON DELETE CASCADE
    op.create_foreign_key(
        'interactions_item_id_fkey',
        'interactions', 'items',
        ['item_id'], ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    op.drop_constraint(
        'interactions_item_id_fkey',
        'interactions',
        type_='foreignkey',
    )
    op.create_foreign_key(
        'interactions_item_id_fkey',
        'interactions', 'items',
        ['item_id'], ['id'],
    )
