from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class Security(Base):
    __tablename__ = "securities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    sector = Column(String(64), nullable=True)
    price = Column(Float, nullable=False)
    shares_outstanding = Column(Float, nullable=True)
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

