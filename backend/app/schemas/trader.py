from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TraderCreate(BaseModel):
    name: str
    desk: Optional[str] = None
    email: Optional[str] = None


class TraderUpdate(BaseModel):
    name: Optional[str] = None
    desk: Optional[str] = None
    email: Optional[str] = None


class TraderResponse(BaseModel):
    id: int
    name: str
    desk: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

