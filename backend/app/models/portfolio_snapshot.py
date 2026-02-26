from sqlalchemy import Column, Date, Float, Integer, Text

from app.database import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_date = Column(Date, nullable=False, unique=True, index=True)
    total_market_value = Column(Float, nullable=False)
    total_cost_basis = Column(Float, nullable=False)
    total_pnl = Column(Float, nullable=False)
    total_pnl_pct = Column(Float, nullable=True)
    breakdown_json = Column(Text, nullable=False)

