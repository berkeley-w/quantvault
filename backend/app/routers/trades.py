import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.audit import audit
from app.core.helpers import serialize_dt
from app.database import get_db
from app.models import RestrictedList, Trade
from app.schemas.trade import RejectRequest, TradeCreate, TradeResponse, TradeUpdate


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trades", tags=["Trades"])


@router.get("", response_model=List[TradeResponse])
def list_trades(
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
            "rejected_at": serialize_dt(t.rejected_at),
            "created_at": serialize_dt(t.created_at),
            "updated_at": serialize_dt(t.updated_at),
        }
        for t in rows
    ]


@router.post("", response_model=TradeResponse)
def create_trade(body: TradeCreate, db: Session = Depends(get_db)):
    restricted = (
        db.query(RestrictedList)
        .filter(RestrictedList.ticker == body.ticker.upper().strip())
        .first()
    )
    if restricted:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Ticker {body.ticker} is on the restricted list. "
                f"Reason: {restricted.reason or 'Not specified'}"
            ),
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
    audit(
        db,
        "TRADE_ADDED",
        "trade",
        t.id,
        f"{t.side} {t.quantity} {t.ticker} @ {t.price} by {t.trader_name}",
    )
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
        "created_at": serialize_dt(t.created_at),
        "updated_at": serialize_dt(t.updated_at),
    }


@router.put("/{id}", response_model=TradeResponse)
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
    audit(
        db,
        "TRADE_EDITED",
        "trade",
        t.id,
        f"Updated trade {t.id}: " + ", ".join(changes),
    )
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
        "rejected_at": serialize_dt(t.rejected_at),
        "created_at": serialize_dt(t.created_at),
        "updated_at": serialize_dt(t.updated_at),
    }


@router.delete("/{id}")
def delete_trade(id: int, db: Session = Depends(get_db)):
    t = db.query(Trade).filter(Trade.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trade not found")
    db.delete(t)
    db.commit()
    audit(db, "TRADE_DELETED", "trade", id, f"Deleted trade {id}")
    return {"detail": "Trade deleted"}


@router.post("/{id}/reject")
def reject_trade(id: int, body: RejectRequest, db: Session = Depends(get_db)):
    t = db.query(Trade).filter(Trade.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trade not found")
    t.status = "REJECTED"
    t.rejection_reason = body.rejection_reason.strip()
    t.rejected_at = datetime.utcnow()
    db.commit()
    db.refresh(t)
    audit(
        db,
        "TRADE_REJECTED",
        "trade",
        t.id,
        f"Rejected trade {t.id}: {t.rejection_reason}",
    )
    return {"detail": "Trade rejected", "id": t.id, "status": t.status}


@router.post("/{id}/reinstate")
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

