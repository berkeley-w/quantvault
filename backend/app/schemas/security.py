from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SecurityCreate(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None
    price: float
    shares_outstanding: Optional[float] = None


class SecurityUpdate(BaseModel):
    ticker: Optional[str] = None
    name: Optional[str] = None
    sector: Optional[str] = None
    price: Optional[float] = None
    shares_outstanding: Optional[float] = None


class SecurityResponse(BaseModel):
    id: int
    ticker: str
    name: str
    sector: Optional[str] = None
    price: float
    shares_outstanding: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

