from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(32), nullable=False, index=True)
    side = Column(String(8), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    trader_name = Column(String(128), nullable=False)
    strategy = Column(String(64), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(16), nullable=False, default="ACTIVE", server_default="ACTIVE")
    rejection_reason = Column(Text, nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

