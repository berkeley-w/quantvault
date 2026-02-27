import logging
from pathlib import Path
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import init_db


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Application factory for QuantVault FastAPI app."""

    settings = get_settings()
    app = FastAPI(title="QuantVault", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import and register all routers
    from app.routers import (  # type: ignore[attr-defined]
        securities,
        traders,
        trades,
        holdings,
        prices,
        portfolio,
        analytics,
        compliance,
        audit,
    )

    for r in [
        securities,
        traders,
        trades,
        holdings,
        prices,
        portfolio,
        analytics,
        compliance,
        audit,
    ]:
        app.include_router(r.router)

    # Static files and SPA
    frontend_dir = Path(__file__).resolve().parent.parent / settings.FRONTEND_DIR
    if frontend_dir.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

        @app.get("/", response_class=FileResponse)
        def serve_frontend() -> FileResponse:
            return FileResponse(str(frontend_dir / "index.html"))

    @app.on_event("startup")
    def startup() -> None:
        init_db()

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "Unhandled error on %s %s", request.method, request.url.path
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app

