import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.audit import audit
from app.models import IndicatorValue, Signal, Strategy
from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)


def evaluate_rsi_mean_reversion(
    db: Session, ticker: str, strategy_id: int, rsi_value: Optional[float]
) -> Optional[Dict[str, Any]]:
    """
    RSI mean-reversion strategy: BUY when RSI < 30, SELL when RSI > 70.
    Returns signal dict if triggered, None otherwise.
    """
    if rsi_value is None:
        return None

    signal_type = None
    strength = 0.0

    if rsi_value < 30:
        signal_type = "BUY"
        # Strength increases as RSI gets lower (more oversold)
        strength = (30 - rsi_value) / 30.0  # Normalized 0-1
    elif rsi_value > 70:
        signal_type = "SELL"
        # Strength increases as RSI gets higher (more overbought)
        strength = (rsi_value - 70) / 30.0  # Normalized 0-1

    if signal_type:
        return {
            "strategy_id": strategy_id,
            "ticker": ticker,
            "signal_type": signal_type,
            "signal_strength": min(strength, 1.0),
            "value": rsi_value,
            "metadata": {"indicator": "RSI_14", "threshold_buy": 30, "threshold_sell": 70},
        }

    return None


def evaluate_active_strategies(db: Session, ticker: str) -> List[Dict[str, Any]]:
    """
    Evaluate all active strategies for a ticker and generate signals.
    Returns list of signal dicts.
    """
    active_strategies = db.query(Strategy).filter(Strategy.is_active.is_(True)).all()
    signals = []

    for strategy in active_strategies:
        # Simple strategy routing based on name
        if "RSI" in strategy.name.upper() or "MEAN_REVERSION" in strategy.name.upper():
            # Get latest RSI value
            latest_rsi = (
                db.query(IndicatorValue)
                .filter(
                    IndicatorValue.ticker == ticker.upper(),
                    IndicatorValue.indicator_type == "RSI_14",
                )
                .order_by(IndicatorValue.timestamp.desc())
                .first()
            )

            if latest_rsi:
                signal = evaluate_rsi_mean_reversion(db, ticker, strategy.id, latest_rsi.value)
                if signal:
                    signals.append(signal)

    return signals


def generate_and_store_signals(db: Session, ticker: str) -> int:
    """
    Evaluate strategies for a ticker and store any generated signals.
    Returns count of signals generated.
    """
    signals = evaluate_active_strategies(db, ticker)

    count = 0
    for signal_data in signals:
        # Check if signal already exists (avoid duplicates)
        existing = (
            db.query(Signal)
            .filter(
                Signal.strategy_id == signal_data["strategy_id"],
                Signal.ticker == ticker.upper(),
                Signal.signal_type == signal_data["signal_type"],
                Signal.timestamp >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
            )
            .first()
        )

        if existing:
            continue

        signal = Signal(
            strategy_id=signal_data["strategy_id"],
            ticker=ticker.upper(),
            signal_type=signal_data["signal_type"],
            signal_strength=signal_data["signal_strength"],
            value=signal_data["value"],
            metadata_json=json.dumps(signal_data.get("metadata", {})),
            timestamp=datetime.utcnow(),
        )
        db.add(signal)
        count += 1

        # Audit log
        audit(
            db,
            "SIGNAL_GENERATED",
            "signal",
            None,
            f"Generated {signal_data['signal_type']} signal for {ticker} from strategy {signal_data['strategy_id']}",
        )

        # Broadcast signal event (fire and forget)
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(manager.broadcast_event(
                    "signal_generated",
                    {
                        "ticker": ticker,
                        "signal_type": signal_data["signal_type"],
                        "strategy_id": signal_data["strategy_id"],
                        "signal_strength": signal_data["signal_strength"],
                    },
                ))
            else:
                loop.run_until_complete(manager.broadcast_event(
                    "signal_generated",
                    {
                        "ticker": ticker,
                        "signal_type": signal_data["signal_type"],
                        "strategy_id": signal_data["strategy_id"],
                        "signal_strength": signal_data["signal_strength"],
                    },
                ))
        except Exception:
            pass  # Don't fail signal generation if WebSocket broadcast fails

    db.commit()
    return count
