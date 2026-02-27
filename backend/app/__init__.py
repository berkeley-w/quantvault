import logging
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
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
        auth,
        securities,
        traders,
        trades,
        holdings,
        prices,
        portfolio,
        analytics,
        compliance,
        audit,
        exports,
    )

    for r in [
        auth,
        securities,
        traders,
        trades,
        holdings,
        prices,
        portfolio,
        analytics,
        compliance,
        audit,
        exports,
    ]:
        app.include_router(r.router)

    # Simple health check
    @app.get("/health", tags=["System"])
    def health_check():
        return {"status": "healthy", "version": "1.0.0"}

    # Static files and SPA catch-all (Vite dist)
    base_dir = Path(__file__).resolve().parent.parent
    frontend_dir = base_dir.parent / "frontend"
    frontend_dist = frontend_dir / "dist"

    if frontend_dist.exists():
        assets_dir = frontend_dist / "assets"
        if assets_dir.exists():
            app.mount(
                "/assets",
                StaticFiles(directory=str(assets_dir)),
                name="assets",
            )

        @app.get("/{full_path:path}", response_class=FileResponse)
        def serve_spa(full_path: str):
            file_path = frontend_dist / full_path
            if file_path.is_file():
                return FileResponse(str(file_path))
            return FileResponse(str(frontend_dist / "index.html"))

    @app.on_event("startup")
    def startup() -> None:
        init_db()

    @app.exception_handler(HTTPException)
    async def http_exc_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return await http_exception_handler(request, exc)

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error_code": "INTERNAL_ERROR",
            },
        )

    return app

