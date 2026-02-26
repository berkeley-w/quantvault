from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


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


class RejectRequest(BaseModel):
    rejection_reason: str

