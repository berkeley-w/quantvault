import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.audit import audit
from app.core.auth import get_current_user, require_admin
from app.core.helpers import serialize_dt
from app.database import get_db
from app.models import RestrictedList, User
from app.schemas.restricted import RestrictedCreate, RestrictedResponse


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/restricted", tags=["Compliance"])


@router.get("", response_model=List[RestrictedResponse])
def list_restricted(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ = user
    rows = db.query(RestrictedList).order_by(RestrictedList.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "ticker": r.ticker,
            "reason": r.reason,
            "added_by": r.added_by,
            "created_at": serialize_dt(r.created_at),
        }
        for r in rows
    ]


@router.post("", response_model=RestrictedResponse)
def add_restricted(
    body: RestrictedCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    r = RestrictedList(
        ticker=body.ticker.upper().strip(),
        reason=body.reason.strip() if body.reason else None,
        added_by=body.added_by.strip() if body.added_by else None,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    audit(
        db,
        "RESTRICTED_ADDED",
        "restricted",
        r.id,
        f"Added {r.ticker} to restricted list",
        user=user,
    )
    return {
        "id": r.id,
        "ticker": r.ticker,
        "reason": r.reason,
        "added_by": r.added_by,
        "created_at": serialize_dt(r.created_at),
    }


@router.delete("/{id}")
def remove_restricted(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    r = db.query(RestrictedList).filter(RestrictedList.id == id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restricted entry not found")
    ticker = r.ticker
    db.delete(r)
    db.commit()
    audit(
        db,
        "RESTRICTED_REMOVED",
        "restricted",
        id,
        f"Removed {ticker} from restricted list",
        user=user,
    )
    return {"detail": "Removed from restricted list"}

