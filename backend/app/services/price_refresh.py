import json
import logging
import time
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.audit import audit
from app.models import CompanyOverview, PortfolioSnapshot, Security
from app.services.alpha_vantage import get_company_overview, get_quote
from app.services.holdings import recompute_holdings
from app.services.portfolio import _compute_portfolio_performance
from app.services.price_history import upsert_today_bar
from app.services.strategy_evaluation import generate_and_store_signals
from app.services.websocket_manager import manager


logger = logging.getLogger(__name__)


def refresh_all_prices(db: Session) -> Dict[str, Any]:
    """
    Fetch quotes for all securities and update their stored price.
    Also refreshes cached company overview data when older than 24 hours
    (or missing) and records a daily portfolio snapshot.

    Uses a 12-second minimum delay between all Alpha Vantage calls to respect
    the free-tier rate limits.
    """
    securities: List[Security] = db.query(Security).order_by(Security.ticker).all()
    updated: List[str] = []
    failed: List[str] = []

    last_call_ts: Optional[float] = None

    def _wait_for_rate_limit() -> None:
        nonlocal last_call_ts
        if last_call_ts is None:
            return
        elapsed = time.time() - last_call_ts
        if elapsed < 12:
            time.sleep(12 - elapsed)

    for sec in securities:
        # Quote
        _wait_for_rate_limit()
        quote = get_quote(sec.ticker)
        last_call_ts = time.time()
        if quote and quote.get("current_price") is not None:
            sec.price = float(quote["current_price"])
            # Also upsert today's daily bar
            upsert_today_bar(db, sec.ticker, quote)
            updated.append(sec.ticker)
        else:
            failed.append(sec.ticker)

        # Company overview (if missing or stale > 24h)
        overview = (
            db.query(CompanyOverview)
            .filter(CompanyOverview.ticker == sec.ticker.upper())
            .first()
        )
        needs_overview = False
        if overview is None:
            needs_overview = True
        elif overview.last_updated is None:
            needs_overview = True
        else:
            age = datetime.utcnow() - overview.last_updated
            if age > timedelta(hours=24):
                needs_overview = True

        if needs_overview:
            _wait_for_rate_limit()
            ov_data = get_company_overview(sec.ticker)
            last_call_ts = time.time()
            if ov_data:
                if overview is None:
                    overview = CompanyOverview(ticker=sec.ticker.upper())
                    db.add(overview)
                overview.shares_outstanding = ov_data.get("SharesOutstanding")
                overview.market_cap = ov_data.get("MarketCapitalization")
                overview.beta = ov_data.get("Beta")
                overview.pe_ratio = ov_data.get("PERatio")
                overview.dividend_yield = ov_data.get("DividendYield")
                overview.fifty_two_week_high = ov_data.get("52WeekHigh")
                overview.fifty_two_week_low = ov_data.get("52WeekLow")
                overview.sector = ov_data.get("Sector")
                overview.industry = ov_data.get("Industry")
                overview.last_updated = datetime.utcnow()

    db.commit()

    # After updating prices and overviews, store/update today's portfolio snapshot
    perf = _compute_portfolio_performance(db)
    today = date.today()
    snapshot = (
        db.query(PortfolioSnapshot)
        .filter(PortfolioSnapshot.snapshot_date == today)
        .first()
    )
    breakdown_json = json.dumps(perf.get("breakdown", []))
    if snapshot is None:
        snapshot = PortfolioSnapshot(
            snapshot_date=today,
            total_market_value=perf["total_market_value"],
            total_cost_basis=perf["total_cost_basis"],
            total_pnl=perf["total_pnl"],
            total_pnl_pct=perf.get("total_pnl_pct"),
            breakdown_json=breakdown_json,
        )
        db.add(snapshot)
    else:
        snapshot.total_market_value = perf["total_market_value"]
        snapshot.total_cost_basis = perf["total_cost_basis"]
        snapshot.total_pnl = perf["total_pnl"]
        snapshot.total_pnl_pct = perf.get("total_pnl_pct")
        snapshot.breakdown_json = breakdown_json

    db.commit()

    # After prices are updated, recompute holdings and evaluate strategies
    recompute_holdings(db)

    for ticker in updated:
        try:
            generate_and_store_signals(db, ticker)
        except Exception as e:
            logger.warning(f"Failed to generate signals for {ticker}: {e}")

    audit(
        db,
        "SECURITIES_PRICES_REFRESHED",
        "security",
        None,
        f"Refreshed prices for {len(updated)} securities; {len(failed)} failed",
    )

    # Broadcast price refresh event (fire and forget)
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.broadcast_event(
                "prices_refreshed",
                {
                    "updated_count": len(updated),
                    "failed_count": len(failed),
                    "updated_tickers": updated,
                },
            ))
        else:
            loop.run_until_complete(manager.broadcast_event(
                "prices_refreshed",
                {
                    "updated_count": len(updated),
                    "failed_count": len(failed),
                    "updated_tickers": updated,
                },
            ))
    except Exception:
        pass  # Don't fail price refresh if WebSocket broadcast fails

    return {
        "updated_count": len(updated),
        "failed_count": len(failed),
        "updated_tickers": updated,
        "failed_tickers": failed,
    }

