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

# Mount all routers so paths match the frontend's /api/v1/* expectations.
# Routers that already define their own resource prefix (e.g. "/traders")
# are included without an extra prefix here to avoid duplicating segments.
v1_router.include_router(auth.router, prefix="/auth")  # /api/v1/auth/...
v1_router.include_router(securities.router)  # /api/v1/securities/...
v1_router.include_router(traders.router)  # /api/v1/traders/...
v1_router.include_router(trades.router)  # /api/v1/trades/...
v1_router.include_router(holdings.router)  # /api/v1/holdings, /api/v1/metrics
v1_router.include_router(prices.router)  # /api/v1/prices/...
v1_router.include_router(price_history.router)  # /api/v1/prices/history...
v1_router.include_router(portfolio.router)  # /api/v1/portfolio/performance, /api/v1/snapshots
v1_router.include_router(analytics.router)  # /api/v1/analytics
v1_router.include_router(technical_analysis.router)  # /api/v1/analytics/technical/...
v1_router.include_router(strategies.router)  # /api/v1/strategies/...
v1_router.include_router(signals.router)  # /api/v1/signals/...
v1_router.include_router(compliance.router)  # /api/v1/restricted/...
v1_router.include_router(audit.router)  # /api/v1/audit/...
v1_router.include_router(exports.router)  # /api/v1/export/...
v1_router.include_router(risk.router)  # /api/v1/risk
