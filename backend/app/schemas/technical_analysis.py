from typing import Any, Dict, List

from pydantic import BaseModel


class IndicatorDataPoint(BaseModel):
    timestamp: str
    value: float | None
    parameters: Dict[str, Any] | None


class TechnicalAnalysisResponse(BaseModel):
    ticker: str
    price_bars: List[Dict[str, Any]]
    indicators: Dict[str, List[IndicatorDataPoint]]
