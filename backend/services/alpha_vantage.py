from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
import os
import time
from typing import Optional, Dict, Any

import logging
import requests

_logger = logging.getLogger(__name__)

_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
_BASE_URL = "https://www.alphavantage.co/query"
_CACHE_TTL_SECONDS = int(os.getenv("ALPHA_VANTAGE_CACHE_TTL", str(15 * 60)))

_quote_cache: Dict[str, Dict[str, Any]] = {}


def _now() -> float:
    return time.time()


def _from_cache(ticker: str) -> Optional[Dict[str, Any]]:
    entry = _quote_cache.get(ticker)
    if not entry:
        _logger.debug("Alpha Vantage cache miss for %s", ticker)
        return None
    if _now() - entry["timestamp"] > _CACHE_TTL_SECONDS:
        _logger.debug("Alpha Vantage cache expired for %s", ticker)
        return None
    _logger.debug("Alpha Vantage cache hit for %s", ticker)
    return entry["data"]


def _save_cache(ticker: str, data: Dict[str, Any]) -> None:
    _quote_cache[ticker] = {"timestamp": _now(), "data": data}


def _request_with_retry(url: str, params: Dict[str, Any], max_retries: int = 2) -> Optional[Dict[str, Any]]:
    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if "Error Message" in data or "Note" in data:
                _logger.warning(
                    "Alpha Vantage API warning: %s",
                    data.get("Error Message") or data.get("Note"),
                )
                return None
            return data
        except requests.exceptions.RequestException as e:
            _logger.warning(
                "Alpha Vantage request failed (attempt %d): %s", attempt + 1, e
            )
            if attempt < max_retries:
                time.sleep(2**attempt)
    return None


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
        _logger.warning("Alpha Vantage API key not configured; skipping quote fetch")
        return None

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": _API_KEY,
    }

    data = _request_with_retry(_BASE_URL, params=params)
    if data is None:
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


def _to_float(value: Any) -> Optional[float]:
    """
    Parse Alpha Vantage numeric fields, handling \"None\" and empty strings.
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s or s.upper() == "NONE":
        return None
    try:
        return float(s)
    except Exception:
        return None


def get_company_overview(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch company overview data from Alpha Vantage OVERVIEW endpoint.

    Returns a dict (or None on error) with keys:
        SharesOutstanding, MarketCapitalization, Beta, PERatio,
        DividendYield, 52WeekHigh, 52WeekLow, Sector, Industry
    """
    symbol = (ticker or "").upper().strip()
    if not symbol or not _API_KEY:
        if not _API_KEY:
            _logger.warning("Alpha Vantage API key not configured; skipping overview fetch")
        return None

    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": _API_KEY,
    }

    data = _request_with_retry(_BASE_URL, params=params)
    if data is None:
        return None

    if not isinstance(data, dict) or not data:
        return None

    return {
        "SharesOutstanding": _to_float(data.get("SharesOutstanding")),
        "MarketCapitalization": _to_float(data.get("MarketCapitalization")),
        "Beta": _to_float(data.get("Beta")),
        "PERatio": _to_float(data.get("PERatio")),
        "DividendYield": _to_float(data.get("DividendYield")),
        "52WeekHigh": _to_float(data.get("52WeekHigh")),
        "52WeekLow": _to_float(data.get("52WeekLow")),
        "Sector": data.get("Sector"),
        "Industry": data.get("Industry"),
    }

