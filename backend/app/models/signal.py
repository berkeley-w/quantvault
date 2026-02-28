from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False, index=True)
    ticker = Column(String(32), nullable=False, index=True)
    signal_type = Column(String(16), nullable=False)  # BUY, SELL, HOLD, ALERT
    signal_strength = Column(Float, nullable=False)  # 0-1 or -1 to 1
    value = Column(Float, nullable=True)  # The indicator value that triggered it
    metadata_json = Column(Text, nullable=True)  # Additional context
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    strategy = relationship("Strategy", backref="signals")
