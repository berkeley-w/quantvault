import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.audit import audit
from app.core.auth import get_current_user, require_admin
from app.core.helpers import apply_sorting, serialize_dt
from app.core.pagination import PaginatedResponse, PaginationParams
from app.database import get_db
from app.models import RestrictedList, Trade, User
from app.schemas.trade import RejectRequest, TradeCreate, TradeResponse, TradeUpdate
from app.services.holdings import recompute_holdings
from app.services.risk import check_trade_risk
from app.services.websocket_manager import manager


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trades", tags=["Trades"])


@router.get("", response_model=PaginatedResponse[TradeResponse])
def list_trades(
    status: str = Query("ALL", description="ACTIVE, REJECTED, or ALL"),
    sort: str = Query("created_at", description="Sort field"),
    order: str = Query("desc", description="Sort order: asc or desc"),
    ticker: str | None = Query(None, description="Filter by ticker"),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ = user
    sort = sort.lower()
    order = order.lower()
    sort_fields = {
        "created_at": Trade.created_at,
        "ticker": Trade.ticker,
        "price": Trade.price,
        "quantity": Trade.quantity,
    }
    q = db.query(Trade)
    if status.upper() == "ACTIVE":
        q = q.filter(Trade.status == "ACTIVE")
    elif status.upper() == "REJECTED":
        q = q.filter(Trade.status == "REJECTED")
    if ticker:
        q = q.filter(Trade.ticker == ticker.upper().strip())
    
    # Get total count before pagination
    total = q.count()
    
    q = apply_sorting(q, Trade, sort, order, sort_fields)
    rows = q.offset(pagination.offset).limit(pagination.limit).all()
    
    items = [
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
    
    return PaginatedResponse.create(items, total, pagination.page, pagination.page_size)


@router.post("", response_model=TradeResponse)
async def create_trade(
    body: TradeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
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
    # Check risk before creating trade
    risk_warnings = check_trade_risk(db, body.ticker, body.side, body.quantity, body.price)

    db.add(t)
    db.commit()
    db.refresh(t)
    audit(
        db,
        "TRADE_ADDED",
        "trade",
        t.id,
        f"{t.side} {t.quantity} {t.ticker} @ {t.price} by {t.trader_name}",
        user=user,
    )
    recompute_holdings(db)
    # Broadcast WebSocket event (fire and forget)
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.broadcast_event(
                "trade_created",
                {
                    "id": t.id,
                    "ticker": t.ticker,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                },
            ))
        else:
            loop.run_until_complete(manager.broadcast_event(
                "trade_created",
                {
                    "id": t.id,
                    "ticker": t.ticker,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                },
            ))
    except Exception:
        pass
    
    response = {
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
    
    # Add risk warnings to response
    if risk_warnings:
        response["risk_warnings"] = risk_warnings
    
    return response


@router.put("/{id}", response_model=TradeResponse)
async def update_trade(
    id: int,
    body: TradeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
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
        user=user,
    )
    recompute_holdings(db)
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.broadcast_event(
                "trade_updated",
                {
                    "id": t.id,
                    "ticker": t.ticker,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                },
            ))
        else:
            loop.run_until_complete(manager.broadcast_event(
                "trade_updated",
                {
                    "id": t.id,
                    "ticker": t.ticker,
                    "side": t.side,
                    "quantity": t.quantity,
                    "price": t.price,
                },
            ))
    except Exception:
        pass
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
async def delete_trade(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    t = db.query(Trade).filter(Trade.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trade not found")
    db.delete(t)
    db.commit()
    audit(db, "TRADE_DELETED", "trade", id, f"Deleted trade {id}", user=user)
    recompute_holdings(db)
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.broadcast_event("trade_deleted", {"id": id}))
        else:
            loop.run_until_complete(manager.broadcast_event("trade_deleted", {"id": id}))
    except Exception:
        pass
    return {"detail": "Trade deleted"}


@router.post("/{id}/reject")
async def reject_trade(
    id: int,
    body: RejectRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
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
        user=user,
    )
    recompute_holdings(db)
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.broadcast_event("trade_rejected", {"id": t.id}))
        else:
            loop.run_until_complete(manager.broadcast_event("trade_rejected", {"id": t.id}))
    except Exception:
        pass
    return {"detail": "Trade rejected", "id": t.id, "status": t.status}


@router.post("/{id}/reinstate")
async def reinstate_trade(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    t = db.query(Trade).filter(Trade.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trade not found")
    t.status = "ACTIVE"
    t.rejection_reason = None
    t.rejected_at = None
    db.commit()
    db.refresh(t)
    audit(
        db,
        "TRADE_REINSTATED",
        "trade",
        t.id,
        f"Reinstated trade {t.id}",
        user=user,
    )
    recompute_holdings(db)
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.broadcast_event("trade_reinstated", {"id": t.id}))
        else:
            loop.run_until_complete(manager.broadcast_event("trade_reinstated", {"id": t.id}))
    except Exception:
        pass
    recompute_holdings(db)
    return {"detail": "Trade reinstated", "id": t.id, "status": t.status}

