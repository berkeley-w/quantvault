from sqlalchemy import Column, DateTime, Float, String

from app.database import Base


class CompanyOverview(Base):
    __tablename__ = "company_overviews"

    ticker = Column(String(32), primary_key=True)
    shares_outstanding = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    beta = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    fifty_two_week_high = Column(Float, nullable=True)
    fifty_two_week_low = Column(Float, nullable=True)
    sector = Column(String(128), nullable=True)
    industry = Column(String(128), nullable=True)
    last_updated = Column(DateTime(timezone=True), nullable=True)

