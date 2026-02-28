"""add_strategy_signal_tables

Revision ID: 0004_strategy_signal
Revises: 0003_add_indicator
Create Date: 2026-02-27 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0004_strategy_signal"
down_revision = "0003_add_indicator"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "strategies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parameters_json", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "signals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("strategy_id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("signal_type", sa.String(length=16), nullable=False),
        sa.Column("signal_strength", sa.Float(), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["strategy_id"], ["strategies.id"]),
    )
    op.create_index(op.f("ix_signals_strategy_id"), "signals", ["strategy_id"], unique=False)
    op.create_index(op.f("ix_signals_ticker"), "signals", ["ticker"], unique=False)
    op.create_index(op.f("ix_signals_timestamp"), "signals", ["timestamp"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_signals_timestamp"), table_name="signals")
    op.drop_index(op.f("ix_signals_ticker"), table_name="signals")
    op.drop_index(op.f("ix_signals_strategy_id"), table_name="signals")
    op.drop_table("signals")
    op.drop_table("strategies")
