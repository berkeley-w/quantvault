from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RestrictedCreate(BaseModel):
    ticker: str
    reason: Optional[str] = None
    added_by: Optional[str] = None


class RestrictedResponse(BaseModel):
    id: int
    ticker: str
    reason: Optional[str] = None
    added_by: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

