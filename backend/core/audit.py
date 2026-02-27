from typing import Optional

from sqlalchemy.orm import Session

from models import AuditLog, User


def audit(
    db: Session,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    details: Optional[str] = None,
    user: Optional[User] = None,
) -> None:
    """
    Add an audit log entry to the current transaction.

    This function does NOT commit; callers are responsible for committing
    so that the business change and audit log are persisted atomically.
    """
    full_details = details
    if user is not None:
        suffix = f" (by {user.username})"
        base = (details or "").rstrip()
        if not base.endswith(suffix):
            full_details = f"{base}{suffix}".strip()

    log = AuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=full_details,
    )
    db.add(log)

