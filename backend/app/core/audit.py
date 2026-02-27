from typing import Optional, TYPE_CHECKING

from sqlalchemy.orm import Session

from app.models import AuditLog

if TYPE_CHECKING:
    from app.models import User


def audit(
    db: Session,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    details: Optional[str] = None,
    user: Optional["User"] = None,
) -> None:
    """
    Persist an audit log entry.

    Mirrors the legacy helper by optionally appending the username to
    the details when a user is provided.
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
    db.commit()

