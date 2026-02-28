import json
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import IndicatorValue, PriceBar
from app.services.technical_analysis import (
    atr,
    bollinger_bands,
    ema,
    macd,
    rsi,
    sma,
)

logger = logging.getLogger(__name__)


def compute_and_store_indicators(
    db: Session,
    ticker: str,
    interval: str = "daily",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Compute all configured indicators for a ticker and store results.
    If indicators already exist for a timestamp, they are updated.
    """
    if start_date is None:
        start_date = date.today() - timedelta(days=365)  # 1 year default
    if end_date is None:
        end_date = date.today()

    # Fetch price bars
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

    if len(bars) < 20:  # Need minimum data
        return {"ticker": ticker, "status": "insufficient_data", "bars_count": len(bars)}

    # Extract arrays
    closes = [b.close for b in bars]
    highs = [b.high for b in bars]
    lows = [b.low for b in bars]
    timestamps = [b.timestamp for b in bars]

    computed = {}

    # SMA indicators (common periods)
    for period in [20, 50, 200]:
        sma_values = sma(closes, period)
        indicator_type = f"SMA_{period}"
        computed[indicator_type] = sma_values
        _store_indicator_values(db, ticker, indicator_type, timestamps, sma_values, None)

    # EMA indicators
    for period in [12, 26, 50]:
        ema_values = ema(closes, period)
        indicator_type = f"EMA_{period}"
        computed[indicator_type] = ema_values
        _store_indicator_values(db, ticker, indicator_type, timestamps, ema_values, None)

    # RSI
    rsi_values = rsi(closes, 14)
    computed["RSI_14"] = rsi_values
    _store_indicator_values(db, ticker, "RSI_14", timestamps, rsi_values, None)

    # MACD
    macd_line, signal_line, histogram = macd(closes, 12, 26, 9)
    computed["MACD"] = {"macd": macd_line, "signal": signal_line, "histogram": histogram}
    _store_indicator_values(db, ticker, "MACD", timestamps, macd_line, {"signal": signal_line, "histogram": histogram})

    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = bollinger_bands(closes, 20, 2.0)
    computed["BB_20"] = {"upper": bb_upper, "middle": bb_middle, "lower": bb_lower}
    _store_indicator_values(db, ticker, "BB_20", timestamps, bb_middle, {"upper": bb_upper, "lower": bb_lower})

    # ATR
    atr_values = atr(highs, lows, closes, 14)
    computed["ATR_14"] = atr_values
    _store_indicator_values(db, ticker, "ATR_14", timestamps, atr_values, None)

    db.commit()

    return {
        "ticker": ticker,
        "status": "success",
        "bars_count": len(bars),
        "indicators_computed": list(computed.keys()),
    }


def _store_indicator_values(
    db: Session,
    ticker: str,
    indicator_type: str,
    timestamps: List[datetime],
    values: List[float | None],
    parameters: Optional[Dict[str, Any]],
) -> None:
    """Store indicator values in the database."""
    for i, (ts, val) in enumerate(zip(timestamps, values)):
        if val is None:
            continue

        # Check if exists
        existing = (
            db.query(IndicatorValue)
            .filter(
                IndicatorValue.ticker == ticker.upper(),
                IndicatorValue.indicator_type == indicator_type,
                IndicatorValue.timestamp == ts,
            )
            .first()
        )

        params_json = json.dumps(parameters) if parameters else None

        if existing:
            existing.value = val
            existing.parameters_json = params_json
        else:
            indicator = IndicatorValue(
                ticker=ticker.upper(),
                indicator_type=indicator_type,
                timestamp=ts,
                value=val,
                parameters_json=params_json,
            )
            db.add(indicator)


def get_indicator_values(
    db: Session,
    ticker: str,
    indicator_types: List[str],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieve cached indicator values for a ticker.
    Returns dict mapping indicator_type to list of {timestamp, value, parameters_json}.
    """
    if start_date is None:
        start_date = date.today() - timedelta(days=180)
    if end_date is None:
        end_date = date.today()

    results: Dict[str, List[Dict[str, Any]]] = {ind: [] for ind in indicator_types}

    for indicator_type in indicator_types:
        values = (
            db.query(IndicatorValue)
            .filter(
                IndicatorValue.ticker == ticker.upper(),
                IndicatorValue.indicator_type == indicator_type,
                IndicatorValue.timestamp >= datetime.combine(start_date, datetime.min.time()),
                IndicatorValue.timestamp <= datetime.combine(end_date, datetime.max.time()),
            )
            .order_by(IndicatorValue.timestamp.asc())
            .all()
        )

        results[indicator_type] = [
            {
                "timestamp": v.timestamp.isoformat(),
                "value": v.value,
                "parameters": json.loads(v.parameters_json) if v.parameters_json else None,
            }
            for v in values
        ]

    return results
