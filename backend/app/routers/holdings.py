import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user
from app.models import Security, Trade, User
from app.schemas.holdings import HoldingResponse, MetricsResponse
from app.services.holdings import _compute_holdings, get_holdings_from_materialized


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Holdings"])


@router.get("/holdings", response_model=List[HoldingResponse])
def get_holdings(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ = user
    # Try materialized first, fallback to computation
    holdings = get_holdings_from_materialized(db)
    if not holdings:
        holdings = _compute_holdings(db)
    return holdings


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ = user
    # Try materialized first, fallback to computation
    holdings_data = get_holdings_from_materialized(db)
    if not holdings_data:
        holdings_data = _compute_holdings(db)
    total_market_value = sum(h["market_value"] for h in holdings_data)
    total_unrealized_pnl = sum(h["unrealized_pnl"] for h in holdings_data)
    positions = [h for h in holdings_data if h["net_quantity"] != 0]
    number_of_positions = len(positions)
    top_holdings = sorted(
        holdings_data, key=lambda x: -abs(x["market_value"])
    )[:10]
    sector_breakdown = {}
    sec_map = {s.ticker: s for s in db.query(Security).all()}
    for h in holdings_data:
        if h["net_quantity"] == 0:
            continue
        sec = sec_map.get(h["ticker"])
        sector = sec.sector if sec and sec.sector else "Unknown"
        sector_breakdown[sector] = sector_breakdown.get(sector, 0) + h[
            "market_value"
        ]
    active_count = db.query(Trade).filter(Trade.status == "ACTIVE").count()
    rejected_count = db.query(Trade).filter(Trade.status == "REJECTED").count()
    total_trades = db.query(Trade).count()
    return {
        "total_market_value": round(total_market_value, 2),
        "total_unrealized_pnl": round(total_unrealized_pnl, 2),
        "number_of_positions": number_of_positions,
        "top_holdings": top_holdings,
        "sector_breakdown": sector_breakdown,
        "trades_active_count": active_count,
        "trades_rejected_count": rejected_count,
        "trades_total_count": total_trades,
    }

