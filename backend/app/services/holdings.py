import logging
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models import Security, Trade


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

