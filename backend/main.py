import os
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List

from dotenv import load_dotenv
from models import (
    Security,
    Trader,
    Trade,
    RestrictedList,
    AuditLog,
    SessionLocal,
    init_db,
)

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
init_db()

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
