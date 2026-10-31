import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.api.health import router as health_router

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("scamshield")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for FastAPI application."""
    logger.info("Starting ScamShield API...")
    # Initialize DB schema for dev/sqlite if needed
    try:
        await init_db()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
    yield
    logger.info("Shutting down ScamShield API...")


app = FastAPI(
    title="ScamShield India API",
    description="Real-time multi-lingual scam detection for Indian digital users (SMS, UPI, WhatsApp, URLs).",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def enforce_payload_limit(request: Request, call_next):
    """Enforce input size cap for privacy protection and DoS mitigation."""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > (settings.MAX_INPUT_CHARS * 4):  # Multi-byte UTF-8 margin
        return JSONResponse(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            content={"detail": f"Payload exceeds maximum allowed size of {settings.MAX_INPUT_CHARS} characters."}
        )
    return await call_next(request)


# Include routers
app.include_router(health_router)


@app.get("/")
async def root():
    return {
        "app": "ScamShield India API",
        "status": "online",
        "docs_url": "/docs",
        "health_url": "/api/health"
    }
