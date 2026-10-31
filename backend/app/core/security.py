import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.user import User

logger = logging.getLogger(__name__)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create signed HMAC-SHA256 JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate application JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None


def verify_google_token(token_str: str) -> Dict[str, Any]:
    """
    Verify Google OAuth 2.0 / OpenID Connect ID token.
    Supports simulated tokens in dev/testing mode.
    """
    # 1. Dev / Test mode bypass for unit tests and local dev
    if settings.ENVIRONMENT in ["development", "testing"] and token_str.startswith("dev-test-token:"):
        # Format: dev-test-token:sub:email:name
        parts = token_str.split(":")
        sub = parts[1] if len(parts) > 1 else "dev-user-sub-12345"
        email = parts[2] if len(parts) > 2 else "dev@scamshield.org"
        return {
            "sub": sub,
            "email": email,
            "name": "Dev User",
            "email_verified": True
        }

    # 2. Production Google verification
    try:
        request = google_requests.Request()
        id_info = id_token.verify_oauth2_token(
            token_str,
            request,
            settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None
        )
        return id_info
    except Exception as e:
        logger.error(f"Google ID token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token."
        )


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Retrieve authenticated user if Authorization header is present; returns None for guests."""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.split("Bearer ")[1].strip()
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None

    try:
        user_id = payload["sub"]
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        return user
    except Exception as e:
        logger.error(f"Error fetching user from token sub: {e}")
        return None


async def get_current_user(
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """Require valid authenticated user."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required."
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require authenticated user with admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required."
        )
    return current_user

