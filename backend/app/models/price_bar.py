from sqlalchemy import Column, DateTime, Float, Index, Integer, String, UniqueConstraint

from app.database import Base


class PriceBar(Base):
    __tablename__ = "price_bars"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(32), nullable=False, index=True)
    interval = Column(String(16), nullable=False, default="daily", server_default="daily")
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)

    __table_args__ = (
        UniqueConstraint("ticker", "interval", "timestamp", name="uq_price_bar_ticker_interval_timestamp"),
        Index("idx_price_bar_ticker_interval_timestamp", "ticker", "interval", "timestamp"),
    )
