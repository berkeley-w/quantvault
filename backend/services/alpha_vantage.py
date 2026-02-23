from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
import os
import time
from typing import Optional, Dict, Any

import requests


_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
_BASE_URL = "https://www.alphavantage.co/query"
_CACHE_TTL_SECONDS = 15 * 60  # 15 minutes

_quote_cache: Dict[str, Dict[str, Any]] = {}


def _now() -> float:
    return time.time()


def _from_cache(ticker: str) -> Optional[Dict[str, Any]]:
    entry = _quote_cache.get(ticker)
    if not entry:
        return None
    if _now() - entry["timestamp"] > _CACHE_TTL_SECONDS:
        return None
    return entry["data"]


def _save_cache(ticker: str, data: Dict[str, Any]) -> None:
    _quote_cache[ticker] = {"timestamp": _now(), "data": data}


def get_quote(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a real-time quote for the given ticker from Alpha Vantage GLOBAL_QUOTE.
    Uses an in-memory cache with a 15-minute TTL to avoid burning API calls.

    Returns a dict with:
        {
            "ticker": str,
            "current_price": float,
            "change": float,
            "change_percent": float,
            "volume": int,
        }
    or None on any error (network, missing API key, bad response).
    """
    symbol = (ticker or "").upper().strip()
    if not symbol:
        return None

    # Try cache first
    cached = _from_cache(symbol)
    if cached is not None:
        return cached

    if not _API_KEY:
        # No API key configured; fail gracefully
        return None

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": _API_KEY,
    }

    try:
        resp = requests.get(_BASE_URL, params=params, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
    except Exception:
        # Network / parsing error
        return None

    try:
        quote = data.get("Global Quote") or data.get("global quote")
        if not quote or "05. price" not in quote:
            return None

        price = float(quote.get("05. price") or 0.0)
        change = float(quote.get("09. change") or 0.0)
        change_pct_raw = quote.get("10. change percent") or quote.get("10. change percent".upper()) or "0%"
        # change percent is like "0.0679%"
        try:
            change_percent = float(str(change_pct_raw).replace("%", "").strip())
        except Exception:
            change_percent = 0.0

        try:
            volume = int(float(quote.get("06. volume") or 0))
        except Exception:
            volume = 0

        result = {
            "ticker": symbol,
            "current_price": price,
            "change": change,
            "change_percent": change_percent,
            "volume": volume,
        }
        _save_cache(symbol, result)
        return result
    except Exception:
        return None

