from typing import Dict, List, Optional

from pydantic import BaseModel


class AnalyticsPosition(BaseModel):
    ticker: str
    net_quantity: float
    avg_cost: float
    current_price: float
    market_value: float
    cost_basis: float
    pnl: float
    pnl_pct: Optional[float] = None
    portfolio_weight_pct: float
    shares_outstanding: Optional[float] = None
    ownership_pct: Optional[float] = None
    beta: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    distance_from_52w_high_pct: Optional[float] = None
    distance_from_52w_low_pct: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None


class PortfolioSummary(BaseModel):
    total_market_value: float
    total_cost_basis: float
    total_pnl: float
    total_pnl_pct: Optional[float] = None
    portfolio_beta: float
    hhi_concentration: float
    concentration_rating: str
    number_of_positions: int
    sector_allocation: Dict[str, Dict[str, float]]


class AnalyticsResponse(BaseModel):
    positions: List[AnalyticsPosition]
    portfolio: PortfolioSummary


class TradeAnalyticsResponse(BaseModel):
    total_trades: int
    buy_trades: int
    sell_trades: int
    total_buy_value: float
    total_sell_value: float
    completed_round_trips: int
    win_count: int
    loss_count: int
    win_rate_pct: Optional[float] = None
    average_win: Optional[float] = None
    average_loss: Optional[float] = None
    largest_win: float
    largest_loss: float
    avg_trade_size: float
    most_traded_ticker: Optional[str] = None
    trades_by_ticker: Dict[str, int]

