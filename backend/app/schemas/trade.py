from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class RiskWarningMessage(BaseModel):
    message: str


class TradeCreate(BaseModel):
    ticker: str
    side: str
    quantity: float
    price: float
    trader_name: str
    strategy: Optional[str] = None
    notes: Optional[str] = None


class TradeUpdate(BaseModel):
    ticker: Optional[str] = None
    side: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    trader_name: Optional[str] = None
    strategy: Optional[str] = None
    notes: Optional[str] = None


class TradeResponse(BaseModel):
    id: int
    ticker: str
    side: str
    quantity: float
    price: float
    trader_name: str
    strategy: Optional[str] = None
    notes: Optional[str] = None
    status: str
    rejection_reason: Optional[str] = None
    rejected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TradeResponseWithWarnings(TradeResponse):
    """Response for POST /trades; may include risk_warnings."""

    risk_warnings: Optional[List[RiskWarningMessage]] = None


class RejectRequest(BaseModel):
    rejection_reason: str

