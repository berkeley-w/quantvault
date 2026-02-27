from alembic import op
import sqlalchemy as sa


revision = "0001_initial_with_users"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "securities",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ticker", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("sector", sa.String(64)),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("shares_outstanding", sa.Float),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "traders",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("desk", sa.String(64)),
        sa.Column("email", sa.String(128)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "trades",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ticker", sa.String(32), nullable=False, index=True),
        sa.Column("side", sa.String(8), nullable=False),
        sa.Column("quantity", sa.Float, nullable=False),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("trader_name", sa.String(128), nullable=False),
        sa.Column("strategy", sa.String(64)),
        sa.Column("notes", sa.Text),
        sa.Column("status", sa.String(16), nullable=False, server_default="ACTIVE"),
        sa.Column("rejection_reason", sa.Text),
        sa.Column("rejected_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_table(
        "restricted_list",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ticker", sa.String(32), nullable=False, index=True),
        sa.Column("reason", sa.Text),
        sa.Column("added_by", sa.String(128)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("entity_type", sa.String(32)),
        sa.Column("entity_id", sa.Integer),
        sa.Column("details", sa.Text),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "company_overviews",
        sa.Column("ticker", sa.String(32), primary_key=True),
        sa.Column("shares_outstanding", sa.Float),
        sa.Column("market_cap", sa.Float),
        sa.Column("beta", sa.Float),
        sa.Column("pe_ratio", sa.Float),
        sa.Column("dividend_yield", sa.Float),
        sa.Column("fifty_two_week_high", sa.Float),
        sa.Column("fifty_two_week_low", sa.Float),
        sa.Column("sector", sa.String(128)),
        sa.Column("industry", sa.String(128)),
        sa.Column("last_updated", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "portfolio_snapshots",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("snapshot_date", sa.Date, nullable=False, unique=True),
        sa.Column("total_market_value", sa.Float, nullable=False),
        sa.Column("total_cost_basis", sa.Float, nullable=False),
        sa.Column("total_pnl", sa.Float, nullable=False),
        sa.Column("total_pnl_pct", sa.Float),
        sa.Column("breakdown_json", sa.Text, nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("email", sa.String(128), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(256), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="1"),
        sa.Column("role", sa.String(32), nullable=False, server_default="trader"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("portfolio_snapshots")
    op.drop_table("company_overviews")
    op.drop_table("audit_log")
    op.drop_table("restricted_list")
    op.drop_table("trades")
    op.drop_table("traders")
    op.drop_table("securities")

