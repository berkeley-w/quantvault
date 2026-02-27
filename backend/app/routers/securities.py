import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.audit import audit
from app.core.helpers import serialize_dt
from app.database import get_db
from app.models import Security
from app.schemas.security import SecurityCreate, SecurityResponse, SecurityUpdate


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/securities", tags=["Securities"])


@router.get("", response_model=List[SecurityResponse])
def list_securities(db: Session = Depends(get_db)):
    rows = db.query(Security).order_by(Security.ticker).all()
    return [
        {
            "id": s.id,
            "ticker": s.ticker,
            "name": s.name,
            "sector": s.sector,
            "price": s.price,
            "shares_outstanding": s.shares_outstanding,
            "created_at": serialize_dt(s.created_at),
            "updated_at": serialize_dt(s.updated_at),
        }
        for s in rows
    ]


@router.post("", response_model=SecurityResponse)
def create_security(body: SecurityCreate, db: Session = Depends(get_db)):
    existing = db.query(Security).filter(Security.ticker == body.ticker.upper()).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Security with ticker {body.ticker} already exists",
        )
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
    audit(
        db,
        "SECURITY_ADDED",
        "security",
        s.id,
        f"Added security {s.ticker} - {s.name}",
    )
    return {
        "id": s.id,
        "ticker": s.ticker,
        "name": s.name,
        "sector": s.sector,
        "price": s.price,
        "shares_outstanding": s.shares_outstanding,
        "created_at": serialize_dt(s.created_at),
        "updated_at": serialize_dt(s.updated_at),
    }


@router.put("/{id}", response_model=SecurityResponse)
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
    audit(
        db,
        "SECURITY_EDITED",
        "security",
        s.id,
        f"Updated {s.ticker}: " + ", ".join(changes),
    )
    return {
        "id": s.id,
        "ticker": s.ticker,
        "name": s.name,
        "sector": s.sector,
        "price": s.price,
        "shares_outstanding": s.shares_outstanding,
        "created_at": serialize_dt(s.created_at),
        "updated_at": serialize_dt(s.updated_at),
    }


@router.delete("/{id}")
def delete_security(id: int, db: Session = Depends(get_db)):
    s = db.query(Security).filter(Security.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Security not found")
    ticker = s.ticker
    db.delete(s)
    db.commit()
    audit(
        db,
        "SECURITY_DELETED",
        "security",
        id,
        f"Deleted security {ticker}",
    )
    return {"detail": "Security deleted"}

