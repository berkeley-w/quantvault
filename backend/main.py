import os
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List, Dict

from dotenv import load_dotenv
from models import (
    Security,
    Trader,
    Trade,
    RestrictedList,
    AuditLog,
    CompanyOverview,
    PortfolioSnapshot,
    SessionLocal,
    init_db,
)
from services import get_quote, get_company_overview
import time
import json
from datetime import date, timedelta, datetime

load_dotenv()

FRONTEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/index.html"))
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _dt(v):
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.isoformat()
    return v


def audit(db: Session, action: str, entity_type: str, entity_id: Optional[int], details: str):
    db.add(AuditLog(action=action, entity_type=entity_type, entity_id=entity_id, details=details))
    db.commit()


# ============== Pydantic schemas ==============
class SecurityCreate(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None
    price: float
    shares_outstanding: Optional[float] = None


class SecurityUpdate(BaseModel):
    ticker: Optional[str] = None
    name: Optional[str] = None
    sector: Optional[str] = None
    price: Optional[float] = None
    shares_outstanding: Optional[float] = None


class TraderCreate(BaseModel):
    name: str
    desk: Optional[str] = None
    email: Optional[str] = None


class TraderUpdate(BaseModel):
    name: Optional[str] = None
    desk: Optional[str] = None
    email: Optional[str] = None


class TradeCreate(BaseModel):
    ticker: str
    side: str
    quantity: float
    price: float
    trader_name: str
    strategy: Optional[str] = None
    notes: Optional[str] = None


class TradeUpdate(BaseModel):
    ticker: Optional[str] = None
    side: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    trader_name: Optional[str] = None
    strategy: Optional[str] = None
    notes: Optional[str] = None


class RestrictedCreate(BaseModel):
    ticker: str
    reason: Optional[str] = None
    added_by: Optional[str] = None


class RejectRequest(BaseModel):
    rejection_reason: str


# ============== Serve frontend ==============
@app.get("/", response_class=FileResponse)
def serve_frontend():
    return FileResponse(FRONTEND_PATH, media_type="text/html")


# ============== Securities ==============
@app.get("/api/securities")
def get_securities(db: Session = Depends(get_db)):
    rows = db.query(Security).order_by(Security.ticker).all()
    return [
        {
            "id": s.id,
            "ticker": s.ticker,
            "name": s.name,
            "sector": s.sector,
            "price": s.price,
            "shares_outstanding": s.shares_outstanding,
            "created_at": _dt(s.created_at),
            "updated_at": _dt(s.updated_at),
        }
        for s in rows
    ]


@app.post("/api/securities")
def create_security(body: SecurityCreate, db: Session = Depends(get_db)):
    existing = db.query(Security).filter(Security.ticker == body.ticker.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Security with ticker {body.ticker} already exists")
    s = Security(
        ticker=body.ticker.upper().strip(),
        name=body.name.strip(),
        sector=body.sector.strip() if body.sector else None,
        price=body.price,
        shares_outstanding=body.shares_outstanding,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    audit(db, "SECURITY_ADDED", "security", s.id, f"Added security {s.ticker} - {s.name}")
    return {"id": s.id, "ticker": s.ticker, "name": s.name, "sector": s.sector, "price": s.price, "shares_outstanding": s.shares_outstanding, "created_at": _dt(s.created_at), "updated_at": _dt(s.updated_at)}


@app.put("/api/securities/{id}")
def update_security(id: int, body: SecurityUpdate, db: Session = Depends(get_db)):
    s = db.query(Security).filter(Security.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Security not found")
    changes = []
    if body.ticker is not None:
        s.ticker = body.ticker.upper().strip()
        changes.append("ticker")
    if body.name is not None:
        s.name = body.name.strip()
        changes.append("name")
    if body.sector is not None:
        s.sector = body.sector.strip() if body.sector else None
        changes.append("sector")
    if body.price is not None:
        s.price = body.price
        changes.append("price")
    if body.shares_outstanding is not None:
        s.shares_outstanding = body.shares_outstanding
        changes.append("shares_outstanding")
    s.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(s)
    audit(db, "SECURITY_EDITED", "security", s.id, f"Updated {s.ticker}: " + ", ".join(changes))
    return {"id": s.id, "ticker": s.ticker, "name": s.name, "sector": s.sector, "price": s.price, "shares_outstanding": s.shares_outstanding, "created_at": _dt(s.created_at), "updated_at": _dt(s.updated_at)}


@app.delete("/api/securities/{id}")
def delete_security(id: int, db: Session = Depends(get_db)):
    s = db.query(Security).filter(Security.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Security not found")
    ticker = s.ticker
    db.delete(s)
    db.commit()
    audit(db, "SECURITY_DELETED", "security", id, f"Deleted security {ticker}")
    return {"detail": "Security deleted"}


# ============== Traders ==============
@app.get("/api/traders")
def get_traders(db: Session = Depends(get_db)):
    rows = db.query(Trader).order_by(Trader.name).all()
    return [
        {"id": t.id, "name": t.name, "desk": t.desk, "email": t.email, "created_at": _dt(t.created_at), "updated_at": _dt(t.updated_at)}
        for t in rows
    ]


@app.post("/api/traders")
def create_trader(body: TraderCreate, db: Session = Depends(get_db)):
    t = Trader(name=body.name.strip(), desk=body.desk.strip() if body.desk else None, email=body.email.strip() if body.email else None)
    db.add(t)
    db.commit()
    db.refresh(t)
    audit(db, "TRADER_ADDED", "trader", t.id, f"Added trader {t.name}")
    return {"id": t.id, "name": t.name, "desk": t.desk, "email": t.email, "created_at": _dt(t.created_at), "updated_at": _dt(t.updated_at)}


@app.put("/api/traders/{id}")
def update_trader(id: int, body: TraderUpdate, db: Session = Depends(get_db)):
    t = db.query(Trader).filter(Trader.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trader not found")
    if body.name is not None:
        t.name = body.name.strip()
    if body.desk is not None:
        t.desk = body.desk.strip() if body.desk else None
    if body.email is not None:
        t.email = body.email.strip() if body.email else None
    t.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(t)
    audit(db, "TRADER_EDITED", "trader", t.id, f"Updated trader {t.name}")
    return {"id": t.id, "name": t.name, "desk": t.desk, "email": t.email, "created_at": _dt(t.created_at), "updated_at": _dt(t.updated_at)}


@app.delete("/api/traders/{id}")
def delete_trader(id: int, db: Session = Depends(get_db)):
    t = db.query(Trader).filter(Trader.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trader not found")
    name = t.name
    db.delete(t)
    db.commit()
    audit(db, "TRADER_DELETED", "trader", id, f"Deleted trader {name}")
    return {"detail": "Trader deleted"}


# ============== Trades ==============
@app.get("/api/trades")
def get_trades(
    status: str = Query("ALL", description="ACTIVE, REJECTED, or ALL"),
    db: Session = Depends(get_db),
):
    q = db.query(Trade).order_by(Trade.created_at.desc())
    if status.upper() == "ACTIVE":
        q = q.filter(Trade.status == "ACTIVE")
    elif status.upper() == "REJECTED":
        q = q.filter(Trade.status == "REJECTED")
    rows = q.all()
    return [
        {
            "id": t.id,
            "ticker": t.ticker,
            "side": t.side,
            "quantity": t.quantity,
            "price": t.price,
            "trader_name": t.trader_name,
            "strategy": t.strategy,
            "notes": t.notes,
            "status": t.status,
            "rejection_reason": t.rejection_reason,
            "rejected_at": _dt(t.rejected_at),
            "created_at": _dt(t.created_at),
            "updated_at": _dt(t.updated_at),
        }
        for t in rows
    ]


@app.post("/api/trades")
def create_trade(body: TradeCreate, db: Session = Depends(get_db)):
    restricted = db.query(RestrictedList).filter(RestrictedList.ticker == body.ticker.upper().strip()).first()
    if restricted:
        raise HTTPException(
            status_code=400,
            detail=f"Ticker {body.ticker} is on the restricted list. Reason: {restricted.reason or 'Not specified'}",
        )
    t = Trade(
        ticker=body.ticker.upper().strip(),
        side=body.side.upper().strip(),
        quantity=body.quantity,
        price=body.price,
        trader_name=body.trader_name.strip(),
        strategy=body.strategy.strip() if body.strategy else None,
        notes=body.notes.strip() if body.notes else None,
        status="ACTIVE",
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    audit(db, "TRADE_ADDED", "trade", t.id, f"{t.side} {t.quantity} {t.ticker} @ {t.price} by {t.trader_name}")
    return {
        "id": t.id,
        "ticker": t.ticker,
        "side": t.side,
        "quantity": t.quantity,
        "price": t.price,
        "trader_name": t.trader_name,
        "strategy": t.strategy,
        "notes": t.notes,
        "status": t.status,
        "rejection_reason": t.rejection_reason,
        "rejected_at": t.rejected_at,
        "created_at": _dt(t.created_at),
        "updated_at": _dt(t.updated_at),
    }


@app.put("/api/trades/{id}")
def update_trade(id: int, body: TradeUpdate, db: Session = Depends(get_db)):
    t = db.query(Trade).filter(Trade.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trade not found")
    if t.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Only ACTIVE trades can be edited")
    changes = []
    if body.ticker is not None:
        t.ticker = body.ticker.upper().strip()
        changes.append("ticker")
    if body.side is not None:
        t.side = body.side.upper().strip()
        changes.append("side")
    if body.quantity is not None:
        t.quantity = body.quantity
        changes.append("quantity")
    if body.price is not None:
        t.price = body.price
        changes.append("price")
    if body.trader_name is not None:
        t.trader_name = body.trader_name.strip()
        changes.append("trader_name")
    if body.strategy is not None:
        t.strategy = body.strategy.strip() if body.strategy else None
        changes.append("strategy")
    if body.notes is not None:
        t.notes = body.notes.strip() if body.notes else None
        changes.append("notes")
    t.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(t)
    audit(db, "TRADE_EDITED", "trade", t.id, f"Updated trade {t.id}: " + ", ".join(changes))
    return {
        "id": t.id,
        "ticker": t.ticker,
        "side": t.side,
        "quantity": t.quantity,
        "price": t.price,
        "trader_name": t.trader_name,
        "strategy": t.strategy,
        "notes": t.notes,
        "status": t.status,
        "rejection_reason": t.rejection_reason,
        "rejected_at": _dt(t.rejected_at),
        "created_at": _dt(t.created_at),
        "updated_at": _dt(t.updated_at),
    }


@app.delete("/api/trades/{id}")
def delete_trade(id: int, db: Session = Depends(get_db)):
    t = db.query(Trade).filter(Trade.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trade not found")
    db.delete(t)
    db.commit()
    audit(db, "TRADE_DELETED", "trade", id, f"Deleted trade {id}")
    return {"detail": "Trade deleted"}


@app.post("/api/trades/{id}/reject")
def reject_trade(id: int, body: RejectRequest, db: Session = Depends(get_db)):
    t = db.query(Trade).filter(Trade.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trade not found")
    t.status = "REJECTED"
    t.rejection_reason = body.rejection_reason.strip()
    t.rejected_at = datetime.utcnow()
    db.commit()
    db.refresh(t)
    audit(db, "TRADE_REJECTED", "trade", t.id, f"Rejected trade {t.id}: {t.rejection_reason}")
    return {"detail": "Trade rejected", "id": t.id, "status": t.status}


@app.post("/api/trades/{id}/reinstate")
def reinstate_trade(id: int, db: Session = Depends(get_db)):
    t = db.query(Trade).filter(Trade.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trade not found")
    t.status = "ACTIVE"
    t.rejection_reason = None
    t.rejected_at = None
    db.commit()
    db.refresh(t)
    audit(db, "TRADE_REINSTATED", "trade", t.id, f"Reinstated trade {t.id}")
    return {"detail": "Trade reinstated", "id": t.id, "status": t.status}


# ============== Holdings (computed) ==============
def _compute_holdings(db: Session):
    active = db.query(Trade).filter(Trade.status == "ACTIVE").all()
    by_ticker = {}
    for t in active:
        if t.ticker not in by_ticker:
            by_ticker[t.ticker] = {"buy_qty": 0.0, "buy_cost": 0.0, "sell_qty": 0.0}
        if t.side.upper() == "BUY":
            by_ticker[t.ticker]["buy_qty"] += t.quantity
            by_ticker[t.ticker]["buy_cost"] += t.quantity * t.price
        else:
            by_ticker[t.ticker]["sell_qty"] += t.quantity
    sec_map = {s.ticker: s for s in db.query(Security).all()}
    out = []
    for ticker, agg in by_ticker.items():
        net_qty = agg["buy_qty"] - agg["sell_qty"]
        avg_cost = (agg["buy_cost"] / agg["buy_qty"]) if agg["buy_qty"] else 0
        sec = sec_map.get(ticker)
        current_price = sec.price if sec else 0
        market_value = net_qty * current_price
        cost_basis = net_qty * avg_cost
        unrealized_pnl = market_value - cost_basis
        out.append({
            "ticker": ticker,
            "net_quantity": net_qty,
            "avg_cost": round(avg_cost, 4),
            "current_price": current_price,
            "market_value": round(market_value, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
        })
    out.sort(key=lambda x: -abs(x["market_value"]))
    return out


@app.get("/api/holdings")
def get_holdings(db: Session = Depends(get_db)):
    return _compute_holdings(db)


# ============== Restricted list ==============
@app.get("/api/restricted")
def get_restricted(db: Session = Depends(get_db)):
    rows = db.query(RestrictedList).order_by(RestrictedList.created_at.desc()).all()
    return [
        {"id": r.id, "ticker": r.ticker, "reason": r.reason, "added_by": r.added_by, "created_at": _dt(r.created_at)}
        for r in rows
    ]


@app.post("/api/restricted")
def create_restricted(body: RestrictedCreate, db: Session = Depends(get_db)):
    r = RestrictedList(
        ticker=body.ticker.upper().strip(),
        reason=body.reason.strip() if body.reason else None,
        added_by=body.added_by.strip() if body.added_by else None,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    audit(db, "RESTRICTED_ADDED", "restricted", r.id, f"Added {r.ticker} to restricted list")
    return {"id": r.id, "ticker": r.ticker, "reason": r.reason, "added_by": r.added_by, "created_at": _dt(r.created_at)}


@app.delete("/api/restricted/{id}")
def delete_restricted(id: int, db: Session = Depends(get_db)):
    r = db.query(RestrictedList).filter(RestrictedList.id == id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restricted entry not found")
    ticker = r.ticker
    db.delete(r)
    db.commit()
    audit(db, "RESTRICTED_REMOVED", "restricted", id, f"Removed {ticker} from restricted list")
    return {"detail": "Removed from restricted list"}


# ============== Audit log ==============
@app.get("/api/audit")
def get_audit(db: Session = Depends(get_db)):
    rows = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(500).all()
    return [
        {"id": a.id, "action": a.action, "entity_type": a.entity_type, "entity_id": a.entity_id, "details": a.details, "timestamp": _dt(a.timestamp)}
        for a in rows
    ]


# ============== Metrics ==============
@app.get("/api/metrics")
def get_metrics(db: Session = Depends(get_db)):
    holdings_data = _compute_holdings(db)
    total_market_value = sum(h["market_value"] for h in holdings_data)
    total_unrealized_pnl = sum(h["unrealized_pnl"] for h in holdings_data)
    positions = [h for h in holdings_data if h["net_quantity"] != 0]
    number_of_positions = len(positions)
    top_holdings = sorted(holdings_data, key=lambda x: -abs(x["market_value"]))[:10]
    sector_breakdown = {}
    sec_map = {s.ticker: s for s in db.query(Security).all()}
    for h in holdings_data:
        if h["net_quantity"] == 0:
            continue
        sec = sec_map.get(h["ticker"])
        sector = sec.sector if sec and sec.sector else "Unknown"
        sector_breakdown[sector] = sector_breakdown.get(sector, 0) + h["market_value"]
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


# ============== Prices & Portfolio Performance (Alpha Vantage) ==============
@app.get("/api/prices/{ticker}")
def get_price(ticker: str, db: Session = Depends(get_db)):
    """
    Return a cached or fresh Alpha Vantage quote for a single ticker.
    Never raises; on error returns fields with None.
    """
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


@app.post("/api/prices/refresh")
def refresh_all_prices(db: Session = Depends(get_db)):
    """
    Fetch quotes for all securities and update their stored price.
    Also refreshes cached company overview data when older than 24 hours
    (or missing) and records a daily portfolio snapshot.

    Uses a 12-second minimum delay between all Alpha Vantage calls to respect
    the free-tier rate limits.
    """
    securities = db.query(Security).order_by(Security.ticker).all()
    updated = []
    failed = []

    last_call_ts: Optional[float] = None

    def _wait_for_rate_limit():
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
    perf = get_portfolio_performance(db)
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

    audit(
        db,
        "SECURITIES_PRICES_REFRESHED",
        "security",
        None,
        f"Refreshed prices for {len(updated)} securities; {len(failed)} failed",
    )
    return {
        "updated_count": len(updated),
        "failed_count": len(failed),
        "updated_tickers": updated,
        "failed_tickers": failed,
    }


def _compute_portfolio_performance(db: Session):
    """
    Internal helper to calculate portfolio performance from all ACTIVE trades
    using current prices stored on the Security table.
    """
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
        (total_pnl / total_cost_basis * 100.0) if total_cost_basis not in (0, 0.0) else None
    )

    result = {
        "total_market_value": round(total_market_value, 2),
        "total_cost_basis": round(total_cost_basis, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl_pct, 4) if total_pnl_pct is not None else None,
        "breakdown": breakdown,
    }
    return result


@app.get("/api/portfolio/performance")
def get_portfolio_performance(db: Session = Depends(get_db)):
    """
    Calculate portfolio performance from all ACTIVE trades using current
    prices stored on the Security table.
    """
    perf = _compute_portfolio_performance(db)
    # Return a version with rounded per-position fields to preserve existing shape
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
                "pnl_pct": round(b["pnl_pct"], 4) if b["pnl_pct"] is not None else None,
            }
            for b in perf["breakdown"]
        ],
    }


# ============== Analytics & Snapshots ==============


@app.get("/api/analytics")
def get_analytics(db: Session = Depends(get_db)):
    perf = _compute_portfolio_performance(db)
    total_market_value = perf["total_market_value"]
    breakdown = perf["breakdown"]

    # Map for company overviews and securities
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
        sector = ov.sector if ov and ov.sector else (sec.sector if sec and sec.sector else None)
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

    # Sector allocation from positions
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


@app.get("/api/trade-analytics")
def get_trade_analytics(db: Session = Depends(get_db)):
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
            "avg_trade_size": (total_notional / total_trades) if total_trades else 0.0,
            "most_traded_ticker": None,
            "trades_by_ticker": trades_by_ticker,
        }

    # Compute realized P&L for sells using average cost from BUY trades
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


@app.get("/api/snapshots")
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

