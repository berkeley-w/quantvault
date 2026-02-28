from typing import List

from pydantic import BaseModel


class PriceBarItem(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float | None


class PriceHistoryResponse(BaseModel):
    ticker: str
    interval: str
    bars: List[PriceBarItem]
