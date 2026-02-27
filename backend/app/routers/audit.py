import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.helpers import serialize_dt
from app.database import get_db
from app.models import AuditLog
from app.schemas.audit import AuditResponse


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/audit", tags=["Audit"])


@router.get("", response_model=List[AuditResponse])
def list_audit(db: Session = Depends(get_db)):
    rows = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(500).all()
    return [
        {
            "id": a.id,
            "action": a.action,
            "entity_type": a.entity_type,
            "entity_id": a.entity_id,
            "details": a.details,
            "timestamp": serialize_dt(a.timestamp),
        }
        for a in rows
    ]

