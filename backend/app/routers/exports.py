import csv
import io
import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models import Security, Trade, User
from app.services.holdings import _compute_holdings
from app.routers.analytics import get_analytics


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/trades")
def export_trades(
    status: str = Query("ALL", description="ACTIVE, REJECTED, or ALL"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    _ = user
    q = db.query(Trade)
    if status.upper() == "ACTIVE":
        q = q.filter(Trade.status == "ACTIVE")
    elif status.upper() == "REJECTED":
        q = q.filter(Trade.status == "REJECTED")
    rows: List[Trade] = q.order_by(Trade.created_at.desc()).all()

    headers = [
        "id",
        "ticker",
        "side",
        "quantity",
        "price",
        "trader_name",
        "strategy",
        "status",
        "created_at",
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for t in rows:
        writer.writerow(
            {
                "id": t.id,
                "ticker": t.ticker,
                "side": t.side,
                "quantity": t.quantity,
                "price": t.price,
                "trader_name": t.trader_name,
                "strategy": t.strategy or "",
                "status": t.status,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
        )
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="trades_export_{datetime.utcnow().date()}.csv"'
        },
    )


@router.get("/holdings")
def export_holdings(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    _ = user
    holdings = _compute_holdings(db)
    headers = [
        "ticker",
        "net_quantity",
        "avg_cost",
        "current_price",
        "market_value",
        "unrealized_pnl",
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for h in holdings:
        writer.writerow(h)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="holdings_export_{datetime.utcnow().date()}.csv"'
        },
    )


@router.get("/analytics")
def export_analytics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> StreamingResponse:
    analytics = get_analytics(db=db, user=user)
    positions = analytics["positions"]
    headers = [
        "ticker",
        "market_value",
        "pnl",
        "pnl_pct",
        "weight_pct",
        "beta",
        "sector",
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for p in positions:
        writer.writerow(
            {
                "ticker": p["ticker"],
                "market_value": p["market_value"],
                "pnl": p["pnl"],
                "pnl_pct": p["pnl_pct"],
                "weight_pct": p["portfolio_weight_pct"],
                "beta": p["beta"],
                "sector": p["sector"],
            }
        )
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="analytics_export_{datetime.utcnow().date()}.csv"'
        },
    )

