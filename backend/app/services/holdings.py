import logging
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models import MaterializedHolding, Security, Trade


logger = logging.getLogger(__name__)


def _compute_holdings(db: Session) -> List[Dict[str, Any]]:
    """Compute current holdings aggregated from ACTIVE trades."""

    active = db.query(Trade).filter(Trade.status == "ACTIVE").all()
    by_ticker: Dict[str, Dict[str, float]] = {}
    for t in active:
        if t.ticker not in by_ticker:
            by_ticker[t.ticker] = {
                "buy_qty": 0.0,
                "buy_cost": 0.0,
                "sell_qty": 0.0,
            }
        if (t.side or "").upper() == "BUY":
            by_ticker[t.ticker]["buy_qty"] += t.quantity
            by_ticker[t.ticker]["buy_cost"] += t.quantity * t.price
        else:
            by_ticker[t.ticker]["sell_qty"] += t.quantity

    sec_map = {s.ticker: s for s in db.query(Security).all()}
    out: List[Dict[str, Any]] = []
    for ticker, agg in by_ticker.items():
        net_qty = agg["buy_qty"] - agg["sell_qty"]
        avg_cost = (agg["buy_cost"] / agg["buy_qty"]) if agg["buy_qty"] else 0
        sec = sec_map.get(ticker)
        current_price = sec.price if sec else 0
        market_value = net_qty * current_price
        cost_basis = net_qty * avg_cost
        unrealized_pnl = market_value - cost_basis
        out.append(
            {
                "ticker": ticker,
                "net_quantity": net_qty,
                "avg_cost": round(avg_cost, 4),
                "current_price": current_price,
                "market_value": round(market_value, 2),
                "unrealized_pnl": round(unrealized_pnl, 2),
            }
        )
    out.sort(key=lambda x: -abs(x["market_value"]))
    return out


def recompute_holdings(db: Session) -> None:
    """
    Recompute holdings and write results to MaterializedHolding table.
    Called after trade create/update/delete/reject/reinstate and price refresh.
    """
    holdings_data = _compute_holdings(db)

    # Clear existing materialized holdings
    db.query(MaterializedHolding).delete()

    # Write new materialized holdings
    for h in holdings_data:
        pnl_pct = None
        if h["cost_basis"] and h["cost_basis"] != 0:
            pnl_pct = (h["unrealized_pnl"] / h["cost_basis"]) * 100.0

        mh = MaterializedHolding(
            ticker=h["ticker"],
            net_quantity=h["net_quantity"],
            average_cost=h["avg_cost"],
            market_value=h["market_value"],
            cost_basis=h["net_quantity"] * h["avg_cost"],
            unrealized_pnl=h["unrealized_pnl"],
            unrealized_pnl_pct=pnl_pct,
            last_updated=datetime.utcnow(),
        )
        db.add(mh)

    db.commit()
    logger.info(f"Recomputed and materialized {len(holdings_data)} holdings")


def get_holdings_from_materialized(db: Session) -> List[Dict[str, Any]]:
    """
    Get holdings from MaterializedHolding table.
    Returns empty list if table is empty (fallback to computation).
    """
    materialized = db.query(MaterializedHolding).all()
    if not materialized:
        return []

    sec_map = {s.ticker: s for s in db.query(Security).all()}
    out: List[Dict[str, Any]] = []
    for mh in materialized:
        sec = sec_map.get(mh.ticker)
        current_price = sec.price if sec else 0
        out.append(
            {
                "ticker": mh.ticker,
                "net_quantity": mh.net_quantity,
                "avg_cost": round(mh.average_cost, 4),
                "current_price": current_price,
                "market_value": round(mh.market_value, 2),
                "unrealized_pnl": round(mh.unrealized_pnl, 2),
            }
        )
    out.sort(key=lambda x: -abs(x["market_value"]))
    return out

