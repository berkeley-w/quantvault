from typing import Any, Dict


def apply_sorting(query, model: Any, sort_field: str, order: str, allowed: Dict[str, Any]):
    """
    Apply ORDER BY to a SQLAlchemy query using a whitelist of allowed columns.
    """
    column = allowed.get(sort_field)
    if column is None:
        return query
    if order == "desc":
        return query.order_by(column.desc())
    return query.order_by(column.asc())

