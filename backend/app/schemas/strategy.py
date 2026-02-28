from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class StrategyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parameters_json: Optional[str] = None
    is_active: bool = True


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters_json: Optional[str] = None
    is_active: Optional[bool] = None


class StrategyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    parameters_json: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
