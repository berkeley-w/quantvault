import logging
from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.helpers import serialize_dt
from app.core.pagination import PaginatedResponse, PaginationParams
from app.database import get_db
from app.models import Signal, User
from app.schemas.signal import SignalResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/signals", tags=["Signals"])


@router.get("", response_model=PaginatedResponse[SignalResponse])
def list_signals(
    ticker: Optional[str] = Query(None, description="Filter by ticker"),
    strategy_id: Optional[int] = Query(None, description="Filter by strategy ID"),
    start: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List signals with optional filtering."""
    _ = user

    q = db.query(Signal)

    if ticker:
        q = q.filter(Signal.ticker == ticker.upper())
    if strategy_id:
        q = q.filter(Signal.strategy_id == strategy_id)

    if start:
        try:
            start_date = date.fromisoformat(start)
            q = q.filter(Signal.timestamp >= datetime.combine(start_date, datetime.min.time()))
        except ValueError:
            pass

    if end:
        try:
            end_date = date.fromisoformat(end)
            q = q.filter(Signal.timestamp <= datetime.combine(end_date, datetime.max.time()))
        except ValueError:
            pass

    total = q.count()
    signals = q.order_by(Signal.timestamp.desc()).offset(pagination.offset).limit(pagination.limit).all()

    items = [
        {
            "id": s.id,
            "strategy_id": s.strategy_id,
            "ticker": s.ticker,
            "signal_type": s.signal_type,
            "signal_strength": s.signal_strength,
            "value": s.value,
            "metadata_json": s.metadata_json,
            "timestamp": serialize_dt(s.timestamp),
            "created_at": serialize_dt(s.created_at),
        }
        for s in signals
    ]
    
    return PaginatedResponse.create(items, total, pagination.page, pagination.page_size)
