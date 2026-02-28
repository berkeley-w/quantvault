from sqlalchemy import Column, DateTime, Float, Index, Integer, String, Text

from app.database import Base


class IndicatorValue(Base):
    __tablename__ = "indicator_values"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(32), nullable=False, index=True)
    indicator_type = Column(String(64), nullable=False, index=True)  # e.g., "SMA_20", "RSI_14", "MACD"
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    value = Column(Float, nullable=True)  # For single-value indicators
    parameters_json = Column(Text, nullable=True)  # JSON for multi-value indicators (MACD, Bollinger)

    __table_args__ = (
        Index("idx_indicator_ticker_type_timestamp", "ticker", "indicator_type", "timestamp"),
    )
