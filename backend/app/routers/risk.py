import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models import User
from app.services.risk import compute_risk_metrics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/risk", tags=["Risk"])


@router.get("")
def get_risk_metrics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get portfolio risk metrics."""
    _ = user
    metrics = compute_risk_metrics(db)
    return metrics
