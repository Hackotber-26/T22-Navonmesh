import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Determine if running SQLite or PostgreSQL
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# SQLite connection args (allow multithreaded / async access in local dev)
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=connect_args,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for acquiring DB session in FastAPI route handlers."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables for local dev / testing."""
    async with engine.begin() as conn:
        # Import models so they are registered with Base.metadata
        from backend.app.models import user, incident, report  # noqa
        await conn.run_sync(Base.metadata.create_all)

