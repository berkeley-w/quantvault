from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class PositionPerformance(BaseModel):
    ticker: str
    net_quantity: float
    avg_cost: float
    current_price: float
    market_value: float
    cost_basis: float
    pnl: float
    pnl_pct: Optional[float] = None


class PortfolioPerformanceResponse(BaseModel):
    total_market_value: float
    total_cost_basis: float
    total_pnl: float
    total_pnl_pct: Optional[float] = None
    breakdown: List[PositionPerformance]


class SnapshotItem(BaseModel):
    date: str
    total_market_value: float
    total_pnl: float
    total_pnl_pct: Optional[float] = None


class SnapshotResponse(BaseModel):
    snapshots: List[SnapshotItem]


class PriceResponse(BaseModel):
    ticker: str
    current_price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[float] = None

