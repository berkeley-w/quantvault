from datetime import datetime
from typing import Any, Optional


def serialize_dt(v: Any) -> Optional[str]:
    """Serialize datetime to ISO format, passthrough for other values."""

    if v is None:
        return None
    if isinstance(v, datetime):
        return v.isoformat()
    return v

