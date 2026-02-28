import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.technical_analysis import TechnicalAnalysisResponse
from app.services.indicator_compute import compute_and_store_indicators, get_indicator_values
from app.services.price_history import get_price_history

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics/technical", tags=["Technical Analysis"])


@router.get("/{ticker}", response_model=TechnicalAnalysisResponse)
def get_technical_analysis(
    ticker: str,
    indicators: str = Query("SMA_20,RSI_14,MACD", description="Comma-separated list of indicators"),
    start: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Get technical analysis data for a ticker.
    If indicators haven't been computed yet, computes and caches them on the fly.
    """
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

    # Parse indicator list
    indicator_list = [ind.strip().upper() for ind in indicators.split(",") if ind.strip()]

    # Get price history
    price_bars = get_price_history(db, ticker, "daily", start_date, end_date)

    # Check if indicators are cached, compute if not
    cached_indicators = get_indicator_values(db, ticker, indicator_list, start_date, end_date)

    # If any indicators are missing, compute them
    needs_compute = False
    for ind in indicator_list:
        if not cached_indicators.get(ind):
            needs_compute = True
            break

    if needs_compute:
        compute_and_store_indicators(db, ticker, "daily", start_date, end_date)
        # Re-fetch after computation
        cached_indicators = get_indicator_values(db, ticker, indicator_list, start_date, end_date)

    return {
        "ticker": ticker.upper(),
        "price_bars": price_bars["bars"],
        "indicators": cached_indicators,
    }
