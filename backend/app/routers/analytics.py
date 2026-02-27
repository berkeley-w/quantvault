import logging
from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models import CompanyOverview, Security, Trade, User
from app.schemas.analytics import AnalyticsResponse, TradeAnalyticsResponse
from app.services.portfolio import _compute_portfolio_performance


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Analytics"])


@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ = user
    perf = _compute_portfolio_performance(db)
    total_market_value = perf["total_market_value"]
    breakdown = perf["breakdown"]

    overviews: Dict[str, CompanyOverview] = {
        c.ticker: c for c in db.query(CompanyOverview).all()
    }
    securities: Dict[str, Security] = {
        s.ticker: s for s in db.query(Security).all()
    }

    positions_out = []
    portfolio_beta = 0.0
    hhi = 0.0

    for b in breakdown:
        ticker = b["ticker"]
        net_qty = b["net_quantity"]
        if net_qty == 0:
            continue

        market_value = b["market_value"]
        cost_basis = b["cost_basis"]
        pnl = b["pnl"]
        pnl_pct = b["pnl_pct"]

        if total_market_value and total_market_value != 0:
            weight_pct = (market_value / total_market_value) * 100.0
        else:
            weight_pct = 0.0

        ov = overviews.get(ticker)
        sec = securities.get(ticker)

        shares_outstanding = ov.shares_outstanding if ov else None
        beta = ov.beta if ov else None
        pe_ratio = ov.pe_ratio if ov else None
        dividend_yield = ov.dividend_yield if ov else None
        fifty_two_week_high = ov.fifty_two_week_high if ov else None
        fifty_two_week_low = ov.fifty_two_week_low if ov else None
        sector = (
            ov.sector
            if ov and ov.sector
            else (sec.sector if sec and sec.sector else None)
        )
        industry = ov.industry if ov else None

        ownership_pct = None
        if shares_outstanding and shares_outstanding > 0:
            ownership_pct = (net_qty / shares_outstanding) * 100.0

        distance_from_high_pct = None
        if fifty_two_week_high and fifty_two_week_high != 0:
            distance_from_high_pct = (
                (b["current_price"] - fifty_two_week_high) / fifty_two_week_high
            ) * 100.0

        distance_from_low_pct = None
        if fifty_two_week_low and fifty_two_week_low != 0:
            distance_from_low_pct = (
                (b["current_price"] - fifty_two_week_low) / fifty_two_week_low
            ) * 100.0

        if beta is not None:
            portfolio_beta += beta * (weight_pct / 100.0)

        if weight_pct is not None:
            hhi += (weight_pct / 100.0) ** 2

        positions_out.append(
            {
                "ticker": ticker,
                "net_quantity": net_qty,
                "avg_cost": b["avg_cost"],
                "current_price": b["current_price"],
                "market_value": market_value,
                "cost_basis": cost_basis,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "portfolio_weight_pct": weight_pct,
                "shares_outstanding": shares_outstanding,
                "ownership_pct": ownership_pct,
                "beta": beta,
                "pe_ratio": pe_ratio,
                "dividend_yield": dividend_yield,
                "fifty_two_week_high": fifty_two_week_high,
                "fifty_two_week_low": fifty_two_week_low,
                "distance_from_52w_high_pct": distance_from_high_pct,
                "distance_from_52w_low_pct": distance_from_low_pct,
                "sector": sector,
                "industry": industry,
            }
        )

    sector_allocation: Dict[str, Dict[str, float]] = {}
    for p in positions_out:
        if total_market_value and total_market_value != 0:
            w_pct = (p["market_value"] / total_market_value) * 100.0
        else:
            w_pct = 0.0
        sec_name = p.get("sector") or "Unknown"
        agg = sector_allocation.setdefault(
            sec_name, {"market_value": 0.0, "weight_pct": 0.0}
        )
        agg["market_value"] += p["market_value"]

    for sec_name, agg in sector_allocation.items():
        if total_market_value and total_market_value != 0:
            agg["weight_pct"] = (agg["market_value"] / total_market_value) * 100.0
        else:
            agg["weight_pct"] = 0.0

    concentration_rating = "Low"
    if hhi > 0.25:
        concentration_rating = "High"
    elif hhi > 0.15:
        concentration_rating = "Moderate"

    portfolio_summary = {
        "total_market_value": perf["total_market_value"],
        "total_cost_basis": perf["total_cost_basis"],
        "total_pnl": perf["total_pnl"],
        "total_pnl_pct": perf["total_pnl_pct"],
        "portfolio_beta": portfolio_beta,
        "hhi_concentration": hhi,
        "concentration_rating": concentration_rating,
        "number_of_positions": len(positions_out),
        "sector_allocation": sector_allocation,
    }

    return {
        "positions": positions_out,
        "portfolio": portfolio_summary,
    }


@router.get("/trade-analytics", response_model=TradeAnalyticsResponse)
def get_trade_analytics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ = user
    trades = db.query(Trade).order_by(Trade.created_at.asc()).all()
    total_trades = len(trades)
    buy_trades = 0
    sell_trades = 0
    total_buy_value = 0.0
    total_sell_value = 0.0
    total_notional = 0.0

    per_ticker: Dict[str, Dict[str, float]] = {}
    trades_by_ticker: Dict[str, int] = {}

    for t in trades:
        side = (t.side or "").upper()
        notional = t.quantity * t.price
        total_notional += notional

        info = per_ticker.setdefault(
            t.ticker,
            {"buy_qty": 0.0, "buy_cost": 0.0, "sell_qty": 0.0},
        )
        trades_by_ticker[t.ticker] = trades_by_ticker.get(t.ticker, 0) + 1

        if side == "BUY":
            buy_trades += 1
            total_buy_value += notional
            info["buy_qty"] += t.quantity
            info["buy_cost"] += notional
        elif side == "SELL":
            sell_trades += 1
            total_sell_value += notional
            info["sell_qty"] += t.quantity

    if sell_trades == 0:
        return {
            "total_trades": total_trades,
            "buy_trades": buy_trades,
            "sell_trades": sell_trades,
            "total_buy_value": total_buy_value,
            "total_sell_value": total_sell_value,
            "completed_round_trips": 0,
            "win_count": 0,
            "loss_count": 0,
            "win_rate_pct": None,
            "average_win": None,
            "average_loss": None,
            "largest_win": 0.0,
            "largest_loss": 0.0,
            "avg_trade_size": (total_notional / total_trades)
            if total_trades
            else 0.0,
            "most_traded_ticker": None,
            "trades_by_ticker": trades_by_ticker,
        }

    realized_pnls = []
    completed_round_trips = 0

    for ticker, info in per_ticker.items():
        buy_qty = info["buy_qty"]
        buy_cost = info["buy_cost"]
        sell_qty = info["sell_qty"]
        if buy_qty > 0 and sell_qty > 0:
            completed_round_trips += 1
        avg_cost = (buy_cost / buy_qty) if buy_qty > 0 else None
        if avg_cost is None:
            continue
        for t in trades:
            if (t.ticker == ticker) and (t.side or "").upper() == "SELL":
                realized_pnl = (t.price - avg_cost) * t.quantity
                realized_pnls.append(realized_pnl)

    win_count = len([p for p in realized_pnls if p > 0])
    loss_count = len([p for p in realized_pnls if p < 0])

    if win_count + loss_count > 0:
        win_rate_pct = (win_count / (win_count + loss_count)) * 100.0
    else:
        win_rate_pct = None

    wins = [p for p in realized_pnls if p > 0]
    losses = [p for p in realized_pnls if p < 0]

    average_win = (sum(wins) / len(wins)) if wins else None
    average_loss = (sum(losses) / len(losses)) if losses else None

    largest_win = max(wins) if wins else 0.0
    largest_loss = min(losses) if losses else 0.0

    avg_trade_size = (total_notional / total_trades) if total_trades else 0.0
    most_traded_ticker = None
    if trades_by_ticker:
        most_traded_ticker = max(trades_by_ticker.items(), key=lambda x: x[1])[0]

    return {
        "total_trades": total_trades,
        "buy_trades": buy_trades,
        "sell_trades": sell_trades,
        "total_buy_value": total_buy_value,
        "total_sell_value": total_sell_value,
        "completed_round_trips": completed_round_trips,
        "win_count": win_count,
        "loss_count": loss_count,
        "win_rate_pct": win_rate_pct,
        "average_win": average_win,
        "average_loss": average_loss,
        "largest_win": largest_win,
        "largest_loss": largest_loss,
        "avg_trade_size": avg_trade_size,
        "most_traded_ticker": most_traded_ticker,
        "trades_by_ticker": trades_by_ticker,
    }

