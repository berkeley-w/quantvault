import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.audit import audit
from app.core.auth import get_current_user, require_admin
from app.core.helpers import serialize_dt
from app.database import get_db
from app.models import Strategy, User
from app.schemas.strategy import StrategyCreate, StrategyResponse, StrategyUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/strategies", tags=["Strategies"])


@router.get("", response_model=List[StrategyResponse])
def list_strategies(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all strategies."""
    _ = user
    strategies = db.query(Strategy).order_by(Strategy.name).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "parameters_json": s.parameters_json,
            "is_active": s.is_active,
            "created_at": serialize_dt(s.created_at),
            "updated_at": serialize_dt(s.updated_at),
        }
        for s in strategies
    ]


@router.post("", response_model=StrategyResponse)
def create_strategy(
    body: StrategyCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Create a new strategy (admin only)."""
    existing = db.query(Strategy).filter(Strategy.name == body.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Strategy with name {body.name} already exists")

    strategy = Strategy(
        name=body.name,
        description=body.description,
        parameters_json=body.parameters_json,
        is_active=body.is_active,
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)

    audit(
        db,
        "STRATEGY_CREATED",
        "strategy",
        strategy.id,
        f"Created strategy {strategy.name}",
        user=admin,
    )

    return {
        "id": strategy.id,
        "name": strategy.name,
        "description": strategy.description,
        "parameters_json": strategy.parameters_json,
        "is_active": strategy.is_active,
        "created_at": serialize_dt(strategy.created_at),
        "updated_at": serialize_dt(strategy.updated_at),
    }


@router.put("/{id}", response_model=StrategyResponse)
def update_strategy(
    id: int,
    body: StrategyUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Update a strategy (admin only)."""
    strategy = db.query(Strategy).filter(Strategy.id == id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    changes = []
    if body.name is not None:
        strategy.name = body.name
        changes.append("name")
    if body.description is not None:
        strategy.description = body.description
        changes.append("description")
    if body.parameters_json is not None:
        strategy.parameters_json = body.parameters_json
        changes.append("parameters_json")
    if body.is_active is not None:
        strategy.is_active = body.is_active
        changes.append("is_active")

    db.commit()
    db.refresh(strategy)

    audit(
        db,
        "STRATEGY_UPDATED",
        "strategy",
        strategy.id,
        f"Updated strategy {strategy.name}: {', '.join(changes)}",
        user=admin,
    )

    return {
        "id": strategy.id,
        "name": strategy.name,
        "description": strategy.description,
        "parameters_json": strategy.parameters_json,
        "is_active": strategy.is_active,
        "created_at": serialize_dt(strategy.created_at),
        "updated_at": serialize_dt(strategy.updated_at),
    }


@router.delete("/{id}")
def delete_strategy(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Delete a strategy (admin only)."""
    strategy = db.query(Strategy).filter(Strategy.id == id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")

    name = strategy.name
    db.delete(strategy)
    db.commit()

    audit(
        db,
        "STRATEGY_DELETED",
        "strategy",
        id,
        f"Deleted strategy {name}",
        user=admin,
    )

    return {"detail": "Strategy deleted"}
