"""add_price_bar_table

Revision ID: 0002_add_price_bar
Revises: 0001_initial_with_users
Create Date: 2026-02-27 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002_add_price_bar"
down_revision = "0001_initial_with_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "price_bars",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("interval", sa.String(length=16), nullable=False, server_default="daily"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("volume", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_price_bars_ticker"), "price_bars", ["ticker"], unique=False)
    op.create_index(op.f("ix_price_bars_timestamp"), "price_bars", ["timestamp"], unique=False)
    op.create_index(
        "idx_price_bar_ticker_interval_timestamp",
        "price_bars",
        ["ticker", "interval", "timestamp"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_price_bar_ticker_interval_timestamp",
        "price_bars",
        ["ticker", "interval", "timestamp"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_price_bar_ticker_interval_timestamp", "price_bars", type_="unique")
    op.drop_index("idx_price_bar_ticker_interval_timestamp", table_name="price_bars")
    op.drop_index(op.f("ix_price_bars_timestamp"), table_name="price_bars")
    op.drop_index(op.f("ix_price_bars_ticker"), table_name="price_bars")
    op.drop_table("price_bars")
