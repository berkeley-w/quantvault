from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuditResponse(BaseModel):
    id: int
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

