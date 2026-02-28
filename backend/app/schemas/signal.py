from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SignalResponse(BaseModel):
    id: int
    strategy_id: int
    ticker: str
    signal_type: str
    signal_strength: float
    value: Optional[float] = None
    metadata_json: Optional[str] = None
    timestamp: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
