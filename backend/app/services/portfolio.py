import logging
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.services.holdings import _compute_holdings, get_holdings_from_materialized


logger = logging.getLogger(__name__)


def _compute_portfolio_performance(db: Session) -> Dict[str, Any]:
    """Calculate portfolio performance from ACTIVE trades and current prices."""

    # Try materialized first, fallback to computation
    holdings_data = get_holdings_from_materialized(db)
    if not holdings_data:
        holdings_data = _compute_holdings(db)
    breakdown = []
    total_market_value = 0.0
    total_cost_basis = 0.0

    for h in holdings_data:
        net_qty = h["net_quantity"]
        cost_basis = net_qty * h["avg_cost"]
        market_value = h["market_value"]
        pnl = market_value - cost_basis
        pnl_pct = (pnl / cost_basis * 100.0) if cost_basis not in (0, 0.0) else None
        total_market_value += market_value
        total_cost_basis += cost_basis
        entry = {
            "ticker": h["ticker"],
            "net_quantity": net_qty,
            "avg_cost": h["avg_cost"],
            "current_price": h["current_price"],
            "market_value": market_value,
            "cost_basis": cost_basis,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
        }
        breakdown.append(entry)

    total_pnl = total_market_value - total_cost_basis
    total_pnl_pct = (
        (total_pnl / total_cost_basis * 100.0)
        if total_cost_basis not in (0, 0.0)
        else None
    )

    result: Dict[str, Any] = {
        "total_market_value": round(total_market_value, 2),
        "total_cost_basis": round(total_cost_basis, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl_pct, 4)
        if total_pnl_pct is not None
        else None,
        "breakdown": breakdown,
    }
    return result

