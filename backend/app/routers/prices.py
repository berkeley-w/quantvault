import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.portfolio import PriceResponse
from app.services.alpha_vantage import get_quote
from app.services.price_refresh import refresh_all_prices


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/prices", tags=["Prices"])


@router.get("/{ticker}", response_model=PriceResponse)
def get_price(ticker: str, db: Session = Depends(get_db)):  # db kept for parity
    """
    Return a cached or fresh Alpha Vantage quote for a single ticker.
    Never raises; on error returns fields with None.
    """
    _ = db
    quote = get_quote(ticker)
    if not quote:
        return {
            "ticker": ticker.upper(),
            "current_price": None,
            "change": None,
            "change_percent": None,
            "volume": None,
        }
    return quote


@router.post("/refresh")
def refresh_prices(db: Session = Depends(get_db)):
    return refresh_all_prices(db)

