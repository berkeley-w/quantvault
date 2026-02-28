"""
Risk metrics service for portfolio risk analysis.
"""
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import CompanyOverview, MaterializedHolding, PortfolioSnapshot, Security

logger = logging.getLogger(__name__)


def compute_portfolio_beta(db: Session, holdings: List[Dict[str, Any]]) -> float:
    """
    Compute portfolio beta weighted by position market value.
    Uses beta from CompanyOverview.
    """
    total_market_value = sum(h.get("market_value", 0) for h in holdings)
    if total_market_value == 0:
        return 0.0

    portfolio_beta = 0.0
    overviews = {c.ticker: c for c in db.query(CompanyOverview).all()}

    for h in holdings:
        market_value = h.get("market_value", 0)
        if market_value == 0:
            continue
        weight = market_value / total_market_value
        overview = overviews.get(h.get("ticker"))
        if overview and overview.beta is not None:
            portfolio_beta += overview.beta * weight

    return round(portfolio_beta, 4)


def compute_var(
    db: Session,
    ticker: Optional[str] = None,
    confidence_level: float = 0.95,
) -> Optional[float]:
    """
    Compute Value at Risk using historical daily returns from PriceBar data.
    Returns VaR as a positive number (loss amount).
    """
    from app.models import PriceBar
    from datetime import date, timedelta

    # Get last 252 trading days (approx 1 year)
    end_date = date.today()
    start_date = end_date - timedelta(days=365)

    query = db.query(PriceBar).filter(
        PriceBar.interval == "daily",
        PriceBar.timestamp >= start_date,
        PriceBar.timestamp <= end_date,
    )

    if ticker:
        query = query.filter(PriceBar.ticker == ticker.upper())

    bars = query.order_by(PriceBar.timestamp.asc()).all()

    if len(bars) < 30:  # Need minimum data
        return None

    # Calculate daily returns
    returns = []
    for i in range(1, len(bars)):
        if bars[i - 1].close and bars[i].close and bars[i - 1].close > 0:
            daily_return = (bars[i].close - bars[i - 1].close) / bars[i - 1].close
            returns.append(daily_return)

    if not returns:
        return None

    # Sort returns and find percentile
    returns_sorted = sorted(returns)
    percentile_index = int((1 - confidence_level) * len(returns_sorted))
    if percentile_index >= len(returns_sorted):
        percentile_index = len(returns_sorted) - 1

    var = abs(returns_sorted[percentile_index])
    return round(var, 6)


def compute_max_drawdown(db: Session) -> Optional[Dict[str, Any]]:
    """
    Compute maximum drawdown from PortfolioSnapshot time series.
    Returns dict with max_drawdown (as decimal), max_drawdown_pct, and dates.
    """
    snapshots = (
        db.query(PortfolioSnapshot)
        .order_by(PortfolioSnapshot.snapshot_date.asc())
        .all()
    )

    if len(snapshots) < 2:
        return None

    peak = snapshots[0].total_market_value
    max_drawdown = 0.0
    max_drawdown_pct = 0.0
    peak_date = snapshots[0].snapshot_date
    trough_date = None

    for snapshot in snapshots:
        if snapshot.total_market_value > peak:
            peak = snapshot.total_market_value
            peak_date = snapshot.snapshot_date

        drawdown = peak - snapshot.total_market_value
        drawdown_pct = (drawdown / peak * 100.0) if peak > 0 else 0.0

        if drawdown > max_drawdown:
            max_drawdown = drawdown
            max_drawdown_pct = drawdown_pct
            trough_date = snapshot.snapshot_date

    return {
        "max_drawdown": round(max_drawdown, 2),
        "max_drawdown_pct": round(max_drawdown_pct, 4),
        "peak_date": peak_date.isoformat() if peak_date else None,
        "trough_date": trough_date.isoformat() if trough_date else None,
    }


def compute_sharpe_ratio(
    db: Session,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> Optional[float]:
    """
    Compute Sharpe ratio from PortfolioSnapshot returns.
    Uses configurable risk-free rate (default 0).
    """
    snapshots = (
        db.query(PortfolioSnapshot)
        .order_by(PortfolioSnapshot.snapshot_date.asc())
        .all()
    )

    if len(snapshots) < 2:
        return None

    # Calculate daily returns
    returns = []
    for i in range(1, len(snapshots)):
        prev_value = snapshots[i - 1].total_market_value
        curr_value = snapshots[i].total_market_value
        if prev_value > 0:
            daily_return = (curr_value - prev_value) / prev_value
            returns.append(daily_return)

    if len(returns) < 2:
        return None

    # Calculate mean and std dev of returns
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    std_dev = variance ** 0.5

    if std_dev == 0:
        return None

    # Annualize
    annual_return = mean_return * periods_per_year
    annual_std = std_dev * (periods_per_year ** 0.5)
    annual_risk_free = risk_free_rate

    sharpe = (annual_return - annual_risk_free) / annual_std
    return round(sharpe, 4)


def compute_concentration_metrics(holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute position concentration metrics including HHI.
    """
    total_market_value = sum(h.get("market_value", 0) for h in holdings)
    if total_market_value == 0:
        return {
            "hhi": 0.0,
            "concentration_rating": "N/A",
            "top_position_pct": 0.0,
            "top_5_positions_pct": 0.0,
        }

    # Calculate weights
    weights = []
    for h in holdings:
        market_value = h.get("market_value", 0)
        if market_value > 0:
            weight = market_value / total_market_value
            weights.append(weight)

    # HHI (Herfindahl-Hirschman Index)
    hhi = sum(w ** 2 for w in weights)

    # Top position and top 5
    sorted_weights = sorted(weights, reverse=True)
    top_position_pct = (sorted_weights[0] * 100.0) if sorted_weights else 0.0
    top_5_pct = (sum(sorted_weights[:5]) * 100.0) if len(sorted_weights) >= 5 else (sum(sorted_weights) * 100.0)

    # Rating
    if hhi > 0.25:
        rating = "High"
    elif hhi > 0.15:
        rating = "Moderate"
    else:
        rating = "Low"

    return {
        "hhi": round(hhi, 4),
        "concentration_rating": rating,
        "top_position_pct": round(top_position_pct, 2),
        "top_5_positions_pct": round(top_5_pct, 2),
    }


def compute_risk_metrics(db: Session) -> Dict[str, Any]:
    """
    Compute all portfolio-level risk metrics.
    """
    # Get holdings
    from app.services.holdings import get_holdings_from_materialized, _compute_holdings

    holdings = get_holdings_from_materialized(db)
    if not holdings:
        holdings = _compute_holdings(db)

    portfolio_beta = compute_portfolio_beta(db, holdings)
    var_95 = compute_var(db, confidence_level=0.95)
    var_99 = compute_var(db, confidence_level=0.99)
    max_dd = compute_max_drawdown(db)
    sharpe = compute_sharpe_ratio(db)
    concentration = compute_concentration_metrics(holdings)

    return {
        "portfolio_beta": portfolio_beta,
        "var_95": var_95,
        "var_99": var_99,
        "max_drawdown": max_dd,
        "sharpe_ratio": sharpe,
        "concentration": concentration,
    }


def check_trade_risk(
    db: Session,
    ticker: str,
    side: str,
    quantity: float,
    price: float,
) -> List[Dict[str, str]]:
    """
    Check risk limits before trade creation.
    Returns list of warnings (empty if no issues).
    For now, logs warnings rather than blocking trades.
    """
    warnings = []

    # Get current holdings
    from app.services.holdings import get_holdings_from_materialized, _compute_holdings

    holdings = get_holdings_from_materialized(db)
    if not holdings:
        holdings = _compute_holdings(db)

    total_market_value = sum(h.get("market_value", 0) for h in holdings)

    # Check single position limit (max 25% of portfolio)
    trade_value = quantity * price
    if side.upper() == "BUY":
        # Find existing position
        existing = next((h for h in holdings if h.get("ticker") == ticker.upper()), None)
        current_value = existing.get("market_value", 0) if existing else 0
        new_value = current_value + trade_value

        if total_market_value > 0:
            new_weight = (new_value / (total_market_value + trade_value)) * 100.0
            if new_weight > 25.0:
                warnings.append(
                    {
                        "severity": "warning",
                        "code": "POSITION_SIZE_LIMIT",
                        "message": f"Trade would result in {new_weight:.2f}% position size (limit: 25%)",
                    }
                )

    # Check sector concentration (if we have sector data)
    securities = {s.ticker: s for s in db.query(Security).all()}
    sec = securities.get(ticker.upper())
    if sec and sec.sector:
        # Calculate sector weight after trade
        sector_value = sum(
            h.get("market_value", 0)
            for h in holdings
            if securities.get(h.get("ticker")) and securities[h.get("ticker")].sector == sec.sector
        )
        if side.upper() == "BUY":
            sector_value += trade_value

        if total_market_value > 0:
            sector_weight = (sector_value / (total_market_value + (trade_value if side.upper() == "BUY" else 0))) * 100.0
            if sector_weight > 40.0:
                warnings.append(
                    {
                        "severity": "warning",
                        "code": "SECTOR_CONCENTRATION",
                        "message": f"Trade would result in {sector_weight:.2f}% sector concentration (limit: 40%)",
                    }
                )

    return warnings
