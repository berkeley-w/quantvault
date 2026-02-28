import logging
import time
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import PriceBar, Security

logger = logging.getLogger(__name__)

settings = get_settings()
_API_KEY = settings.ALPHA_VANTAGE_API_KEY
_BASE_URL = "https://www.alphavantage.co/query"


def _wait_for_rate_limit(last_call_ts: Optional[float]) -> float:
    """Wait if needed to respect Alpha Vantage rate limits (12s between calls)."""
    if last_call_ts is None:
        return time.time()
    elapsed = time.time() - last_call_ts
    if elapsed < 12:
        time.sleep(12 - elapsed)
    return time.time()


def fetch_daily_ohlcv(ticker: str) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch daily OHLCV data from Alpha Vantage TIME_SERIES_DAILY_ADJUSTED.
    Returns a list of dicts with keys: date, open, high, low, close, volume.
    """
    if not _API_KEY:
        logger.warning("Alpha Vantage API key not configured")
        return None

    symbol = ticker.upper().strip()
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "apikey": _API_KEY,
        "outputsize": "full",  # Get full history
    }

    try:
        resp = requests.get(_BASE_URL, params=params, timeout=15)
        if resp.status_code != 200:
            logger.warning(f"Alpha Vantage request failed: {resp.status_code}")
            return None
        data = resp.json()

        if "Error Message" in data or "Note" in data:
            logger.warning(
                f"Alpha Vantage API warning: {data.get('Error Message') or data.get('Note')}"
            )
            return None

        time_series = data.get("Time Series (Daily)") or data.get("time series (daily)")
        if not time_series:
            return None

        bars = []
        for date_str, values in time_series.items():
            try:
                bar_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                bars.append(
                    {
                        "date": bar_date,
                        "open": float(values.get("1. open", 0)),
                        "high": float(values.get("2. high", 0)),
                        "low": float(values.get("3. low", 0)),
                        "close": float(values.get("5. adjusted close") or values.get("4. close", 0)),
                        "volume": float(values.get("6. volume", 0)),
                    }
                )
            except (ValueError, KeyError, TypeError) as e:
                logger.debug(f"Skipping invalid bar for {date_str}: {e}")
                continue

        bars.sort(key=lambda x: x["date"])
        return bars
    except Exception as e:
        logger.error(f"Error fetching daily OHLCV for {ticker}: {e}")
        return None


def backfill_ticker(db: Session, ticker: str) -> Dict[str, Any]:
    """
    Backfill historical daily bars for a ticker.
    Skips rows that already exist (based on unique constraint).
    """
    logger.info(f"Backfilling price history for {ticker}")

    bars_data = fetch_daily_ohlcv(ticker)
    if not bars_data:
        return {"ticker": ticker, "status": "failed", "message": "Failed to fetch data"}

    inserted = 0
    skipped = 0

    for bar_data in bars_data:
        # Check if already exists
        existing = (
            db.query(PriceBar)
            .filter(
                PriceBar.ticker == ticker.upper(),
                PriceBar.interval == "daily",
                PriceBar.timestamp == datetime.combine(bar_data["date"], datetime.min.time()),
            )
            .first()
        )

        if existing:
            skipped += 1
            continue

        bar = PriceBar(
            ticker=ticker.upper(),
            interval="daily",
            timestamp=datetime.combine(bar_data["date"], datetime.min.time()),
            open=bar_data["open"],
            high=bar_data["high"],
            low=bar_data["low"],
            close=bar_data["close"],
            volume=bar_data["volume"],
        )
        db.add(bar)
        inserted += 1

    db.commit()
    logger.info(f"Backfilled {ticker}: {inserted} inserted, {skipped} skipped")
    return {
        "ticker": ticker,
        "status": "success",
        "inserted": inserted,
        "skipped": skipped,
    }


def backfill_all_securities(db: Session) -> Dict[str, Any]:
    """Backfill historical data for all securities, respecting rate limits."""
    securities = db.query(Security).order_by(Security.ticker).all()
    results = []
    last_call_ts: Optional[float] = None

    for sec in securities:
        last_call_ts = _wait_for_rate_limit(last_call_ts)
        result = backfill_ticker(db, sec.ticker)
        results.append(result)
        last_call_ts = time.time()

    return {
        "total": len(securities),
        "results": results,
    }


def get_price_history(
    db: Session,
    ticker: str,
    interval: str = "daily",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[Dict[str, Any]]:
    """
    Get price history for a ticker within a date range.
    Defaults to last 6 months if no range specified.
    """
    if start_date is None:
        start_date = date.today() - timedelta(days=180)  # 6 months
    if end_date is None:
        end_date = date.today()

    bars = (
        db.query(PriceBar)
        .filter(
            PriceBar.ticker == ticker.upper(),
            PriceBar.interval == interval,
            PriceBar.timestamp >= datetime.combine(start_date, datetime.min.time()),
            PriceBar.timestamp <= datetime.combine(end_date, datetime.max.time()),
        )
        .order_by(PriceBar.timestamp.asc())
        .all()
    )

    return [
        {
            "timestamp": bar.timestamp.isoformat(),
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume,
        }
        for bar in bars
    ]


def upsert_today_bar(db: Session, ticker: str, quote: Dict[str, Any]) -> None:
    """Insert or update today's daily bar from a quote."""
    if not quote or quote.get("current_price") is None:
        return

    today = date.today()
    timestamp = datetime.combine(today, datetime.min.time())

    existing = (
        db.query(PriceBar)
        .filter(
            PriceBar.ticker == ticker.upper(),
            PriceBar.interval == "daily",
            PriceBar.timestamp == timestamp,
        )
        .first()
    )

    price = float(quote["current_price"])
    volume = quote.get("volume") or 0.0

    if existing:
        # Update existing bar
        existing.open = price  # Use current price as open if we don't have intraday data
        existing.high = max(existing.high, price)
        existing.low = min(existing.low, price)
        existing.close = price
        existing.volume = float(volume)
    else:
        # Create new bar
        bar = PriceBar(
            ticker=ticker.upper(),
            interval="daily",
            timestamp=timestamp,
            open=price,
            high=price,
            low=price,
            close=price,
            volume=float(volume),
        )
        db.add(bar)

    db.commit()
