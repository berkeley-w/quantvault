import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.audit import audit
from app.core.helpers import serialize_dt
from app.database import get_db
from app.models import Trader
from app.schemas.trader import TraderCreate, TraderResponse, TraderUpdate


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/traders", tags=["Traders"])


@router.get("", response_model=List[TraderResponse])
def list_traders(db: Session = Depends(get_db)):
    rows = db.query(Trader).order_by(Trader.name).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "desk": t.desk,
            "email": t.email,
            "created_at": serialize_dt(t.created_at),
            "updated_at": serialize_dt(t.updated_at),
        }
        for t in rows
    ]


@router.post("", response_model=TraderResponse)
def create_trader(body: TraderCreate, db: Session = Depends(get_db)):
    t = Trader(
        name=body.name.strip(),
        desk=body.desk.strip() if body.desk else None,
        email=body.email.strip() if body.email else None,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    audit(db, "TRADER_ADDED", "trader", t.id, f"Added trader {t.name}")
    return {
        "id": t.id,
        "name": t.name,
        "desk": t.desk,
        "email": t.email,
        "created_at": serialize_dt(t.created_at),
        "updated_at": serialize_dt(t.updated_at),
    }


@router.put("/{id}", response_model=TraderResponse)
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
    return {
        "id": t.id,
        "name": t.name,
        "desk": t.desk,
        "email": t.email,
        "created_at": serialize_dt(t.created_at),
        "updated_at": serialize_dt(t.updated_at),
    }


@router.delete("/{id}")
def delete_trader(id: int, db: Session = Depends(get_db)):
    t = db.query(Trader).filter(Trader.id == id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Trader not found")
    name = t.name
    db.delete(t)
    db.commit()
    audit(db, "TRADER_DELETED", "trader", id, f"Deleted trader {name}")
    return {"detail": "Trader deleted"}

