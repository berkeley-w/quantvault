from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config import get_settings


settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for FastAPI dependency."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database schema by running Alembic migrations.

    This replaces the old create_all() approach. On startup, any pending
    migrations are applied automatically.

    To create a new migration:
        1. Make changes to models in app/models/
        2. Run: alembic revision --autogenerate -m "description"
        3. Review the generated migration in alembic/versions/
        4. Run: alembic upgrade head (or migrations run automatically on startup)
    """
    from alembic.config import Config
    from alembic import command

    # Import models so they are registered with SQLAlchemy metadata
    from app import models as _models  # noqa: F401

    _ = _models

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    # Run migrations to bring database up to date
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        # If migrations fail, log but don't crash (for first-time setup)
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Migration failed: {e}. This may be normal on first run.")
        # Fallback to create_all for initial setup if migrations don't exist
        Base.metadata.create_all(bind=engine)

