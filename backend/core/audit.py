from typing import Optional

from sqlalchemy.orm import Session

from models import AuditLog


def audit(
    db: Session,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    details: Optional[str] = None,
) -> None:
    """
    Add an audit log entry to the current transaction.

    This function does NOT commit; callers are responsible for committing
    so that the business change and audit log are persisted atomically.
    """
    log = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(log)

