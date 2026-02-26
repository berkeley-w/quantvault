from typing import Dict, List

from pydantic import BaseModel


class HoldingResponse(BaseModel):
    ticker: str
    net_quantity: float
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float


class MetricsResponse(BaseModel):
    total_market_value: float
    total_unrealized_pnl: float
    number_of_positions: int
    trades_active_count: int
    trades_rejected_count: int
    trades_total_count: int
    top_holdings: List[HoldingResponse]
    sector_breakdown: Dict[str, float]

