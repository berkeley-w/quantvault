import logging
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.helpers import serialize_dt
from app.core.pagination import PaginatedResponse, PaginationParams
from app.database import get_db
from app.models import AuditLog, User
from app.schemas.audit import AuditResponse


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/audit", tags=["Audit"])


@router.get("", response_model=PaginatedResponse[AuditResponse])
def list_audit(
    action: str | None = Query(None, description="Filter by action code"),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ = user
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action == action)
    total = q.count()
    rows = q.order_by(AuditLog.timestamp.desc()).offset(pagination.offset).limit(pagination.limit).all()
    
    items = [
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
    
    return PaginatedResponse.create(items, total, pagination.page, pagination.page_size)

