"""add_materialized_holding_table

Revision ID: 0005_materialized_holding
Revises: 0004_strategy_signal
Create Date: 2026-02-27 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0005_materialized_holding"
down_revision = "0004_strategy_signal"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "materialized_holdings",
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("net_quantity", sa.Float(), nullable=False),
        sa.Column("average_cost", sa.Float(), nullable=False),
        sa.Column("market_value", sa.Float(), nullable=False),
        sa.Column("cost_basis", sa.Float(), nullable=False),
        sa.Column("unrealized_pnl", sa.Float(), nullable=False),
        sa.Column("unrealized_pnl_pct", sa.Float(), nullable=True),
        sa.Column("last_updated", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("ticker"),
    )


def downgrade() -> None:
    op.drop_table("materialized_holdings")
