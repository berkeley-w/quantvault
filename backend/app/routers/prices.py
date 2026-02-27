import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_admin
from app.database import SessionLocal, get_db
from app.models import User
from app.schemas.portfolio import PriceResponse
from app.services.alpha_vantage import get_quote
from app.services.price_refresh import refresh_all_prices


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/prices", tags=["Prices"])

_refresh_status = {
    "running": False,
    "last_result": None,
    "last_run_at": None,
}


def _run_price_refresh_background() -> None:
    db = SessionLocal()
    try:
        result = refresh_all_prices(db)
        _refresh_status["last_result"] = result
        from datetime import datetime

        _refresh_status["last_run_at"] = datetime.utcnow().isoformat()
    except Exception as e:  # pragma: no cover - defensive
        _refresh_status["last_result"] = {"error": str(e)}
    finally:
        _refresh_status["running"] = False
        db.close()


@router.get("/{ticker}", response_model=PriceResponse)
def get_price(
    ticker: str,
    db: Session = Depends(get_db),  # db kept for parity
    user: User = Depends(get_current_user),
):
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
def refresh_prices(
    background_tasks: BackgroundTasks,
    admin: User = Depends(require_admin),
):
    _ = admin
    if _refresh_status["running"]:
        raise HTTPException(status_code=409, detail="Price refresh already in progress")
    _refresh_status["running"] = True
    background_tasks.add_task(_run_price_refresh_background)
    return {"status": "started", "message": "Price refresh started in background"}


@router.get("/refresh/status")
def get_refresh_status(user: User = Depends(get_current_user)):
    _ = user
    return _refresh_status

