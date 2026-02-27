import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PortfolioSnapshot
from app.schemas.portfolio import PortfolioPerformanceResponse, SnapshotResponse
from app.services.portfolio import _compute_portfolio_performance


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Portfolio"])


@router.get(
    "/portfolio/performance",
    response_model=PortfolioPerformanceResponse,
)
def get_performance(db: Session = Depends(get_db)):
    """
    Calculate portfolio performance from all ACTIVE trades using current
    prices stored on the Security table.
    """
    perf = _compute_portfolio_performance(db)
    return {
        "total_market_value": perf["total_market_value"],
        "total_cost_basis": perf["total_cost_basis"],
        "total_pnl": perf["total_pnl"],
        "total_pnl_pct": perf["total_pnl_pct"],
        "breakdown": [
            {
                **b,
                "market_value": round(b["market_value"], 2),
                "cost_basis": round(b["cost_basis"], 2),
                "pnl": round(b["pnl"], 2),
                "pnl_pct": round(b["pnl_pct"], 4)
                if b["pnl_pct"] is not None
                else None,
            }
            for b in perf["breakdown"]
        ],
    }


@router.get("/snapshots", response_model=SnapshotResponse)
def get_snapshots(db: Session = Depends(get_db)):
    rows = (
        db.query(PortfolioSnapshot)
        .order_by(PortfolioSnapshot.snapshot_date.asc())
        .all()
    )
    return {
        "snapshots": [
            {
                "date": r.snapshot_date.isoformat(),
                "total_market_value": r.total_market_value,
                "total_pnl": r.total_pnl,
                "total_pnl_pct": r.total_pnl_pct,
            }
            for r in rows
        ]
    }

