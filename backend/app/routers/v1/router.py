"""
V1 API Router - All endpoints at /api/v1/
Maintains backward compatibility by keeping original /api/ routes
"""
from fastapi import APIRouter

from app.routers import (
    auth,
    securities,
    traders,
    trades,
    holdings,
    prices,
    price_history,
    portfolio,
    analytics,
    technical_analysis,
    strategies,
    signals,
    compliance,
    audit,
    exports,
    risk,
)

# Create v1 router
v1_router = APIRouter(prefix="/api/v1")

# Mount all routers, stripping their /api prefix and adding /api/v1
v1_router.include_router(auth.router, prefix="/auth")
v1_router.include_router(securities.router, prefix="/securities")
v1_router.include_router(traders.router, prefix="/traders")
v1_router.include_router(trades.router, prefix="/trades")
v1_router.include_router(holdings.router, prefix="")
v1_router.include_router(prices.router, prefix="/prices")
v1_router.include_router(price_history.router, prefix="/prices")
v1_router.include_router(portfolio.router, prefix="")
v1_router.include_router(analytics.router, prefix="")
v1_router.include_router(technical_analysis.router, prefix="/analytics/technical")
v1_router.include_router(strategies.router, prefix="/strategies")
v1_router.include_router(signals.router, prefix="/signals")
v1_router.include_router(compliance.router, prefix="/restricted")
v1_router.include_router(audit.router, prefix="/audit")
v1_router.include_router(exports.router, prefix="/export")
v1_router.include_router(risk.router, prefix="/risk")
