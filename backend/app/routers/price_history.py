import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_admin
from app.database import get_db
from app.models import User
from app.schemas.price_history import PriceHistoryResponse
from app.services.price_history import backfill_all_securities, backfill_ticker, get_price_history

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/prices", tags=["Price History"])


@router.get("/{ticker}/history", response_model=PriceHistoryResponse)
def get_ticker_history(
    ticker: str,
    interval: str = Query("daily", description="Time interval (daily, 1h, 5m, etc.)"),
    start: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get price history for a ticker within a date range."""
    _ = user
    start_date = None
    end_date = None

    if start:
        try:
            start_date = date.fromisoformat(start)
        except ValueError:
            start_date = None
    if end:
        try:
            end_date = date.fromisoformat(end)
        except ValueError:
            end_date = None

    bars = get_price_history(db, ticker, interval, start_date, end_date)
    return {"ticker": ticker.upper(), "interval": interval, "bars": bars}


@router.post("/backfill/{ticker}")
def backfill_single_ticker(
    ticker: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Backfill historical price data for a single ticker (admin only)."""
    _ = admin
    result = backfill_ticker(db, ticker)
    return result


@router.post("/backfill")
def backfill_all_tickers(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Backfill historical price data for all securities (admin only)."""
    _ = admin
    result = backfill_all_securities(db)
    return result
