"""add_indicator_value_table

Revision ID: 0003_add_indicator
Revises: 0002_add_price_bar
Create Date: 2026-02-27 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003_add_indicator"
down_revision = "0002_add_price_bar"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "indicator_values",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("indicator_type", sa.String(length=64), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("parameters_json", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_indicator_values_ticker"), "indicator_values", ["ticker"], unique=False)
    op.create_index(
        op.f("ix_indicator_values_indicator_type"), "indicator_values", ["indicator_type"], unique=False
    )
    op.create_index(
        op.f("ix_indicator_values_timestamp"), "indicator_values", ["timestamp"], unique=False
    )
    op.create_index(
        "idx_indicator_ticker_type_timestamp",
        "indicator_values",
        ["ticker", "indicator_type", "timestamp"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_indicator_ticker_type_timestamp", table_name="indicator_values")
    op.drop_index(op.f("ix_indicator_values_timestamp"), table_name="indicator_values")
    op.drop_index(op.f("ix_indicator_values_indicator_type"), table_name="indicator_values")
    op.drop_index(op.f("ix_indicator_values_ticker"), table_name="indicator_values")
    op.drop_table("indicator_values")
