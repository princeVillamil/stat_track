"""add_on_update_cascade_to_players

Revision ID: e5a6dee82bcf
Revises: 926196f713b8
Create Date: 2026-04-14 02:22:28.484712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5a6dee82bcf'
down_revision: Union[str, None] = '926196f713b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update leaderboard_snapshots
    op.drop_constraint('leaderboard_snapshots_account_name_fkey', 'leaderboard_snapshots', type_='foreignkey')
    op.create_foreign_key(
        'leaderboard_snapshots_account_name_fkey',
        'leaderboard_snapshots', 'players',
        ['account_name'], ['account_name'],
        onupdate='CASCADE'
    )

    # 2. Update mmr_history
    op.drop_constraint('mmr_history_account_name_fkey', 'mmr_history', type_='foreignkey')
    op.create_foreign_key(
        'mmr_history_account_name_fkey',
        'mmr_history', 'players',
        ['account_name'], ['account_name'],
        onupdate='CASCADE'
    )

    # 3. Update player_hero_stats
    op.drop_constraint('player_hero_stats_account_name_fkey', 'player_hero_stats', type_='foreignkey')
    op.create_foreign_key(
        'player_hero_stats_account_name_fkey',
        'player_hero_stats', 'players',
        ['account_name'], ['account_name'],
        onupdate='CASCADE'
    )


def downgrade() -> None:
    # Reverse mmr_history
    op.drop_constraint('mmr_history_account_name_fkey', 'mmr_history', type_='foreignkey')
    op.create_foreign_key(
        'mmr_history_account_name_fkey',
        'mmr_history', 'players',
        ['account_name'], ['account_name']
    )

    # Reverse leaderboard_snapshots
    op.drop_constraint('leaderboard_snapshots_account_name_fkey', 'leaderboard_snapshots', type_='foreignkey')
    op.create_foreign_key(
        'leaderboard_snapshots_account_name_fkey',
        'leaderboard_snapshots', 'players',
        ['account_name'], ['account_name']
    )

    # Reverse player_hero_stats
    op.drop_constraint('player_hero_stats_account_name_fkey', 'player_hero_stats', type_='foreignkey')
    op.create_foreign_key(
        'player_hero_stats_account_name_fkey',
        'player_hero_stats', 'players',
        ['account_name'], ['account_name']
    )
