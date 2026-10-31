import logging
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint verifying database connectivity and service status."""
    db_status = "unknown"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health check DB error: {e}")
        db_status = f"error: {str(e)}"

    redis_status = "disabled"
    if settings.REDIS_ENABLED:
        try:
            import redis.asyncio as aioredis
            r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            await r.ping()
            await r.close()
            redis_status = "connected"
        except Exception as e:
            logger.warning(f"Health check Redis error: {e}")
            redis_status = f"unreachable: {str(e)}"

    is_healthy = db_status == "connected"
    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ok" if is_healthy else "degraded",
            "environment": settings.ENVIRONMENT,
            "database": db_status,
            "redis": redis_status,
            "versions": {
                "model_version": settings.MODEL_VERSION,
                "rules_version": settings.RULES_VERSION,
            },
        }
    )
