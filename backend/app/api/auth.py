import logging
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.security import (
    verify_google_token,
    create_access_token,
    get_current_user,
    get_current_admin
)
from backend.app.models.user import User
from backend.app.models.incident import Incident

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["auth"])


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(..., description="Google OAuth 2.0 / OpenID Connect ID token")
    preferred_lang: Optional[str] = Field(default="en", description="Preferred UI language")


class UserResponse(BaseModel):
    id: str
    email: Optional[str]
    role: str
    preferred_lang: str
    created_at: Optional[str] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserIncidentHistoryItem(BaseModel):
    id: str
    input_type: str
    category: str
    risk_level: str
    risk_score: float
    reason_codes: List[str]
    language: str
    domain_hash: Optional[str]
    user_action_state: Optional[str]
    created_at: str


@router.post("/auth/google", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def google_auth(
    payload: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user via Google ID Token.
    Scopes: openid email profile only.
    Assigns role 'admin' if email is in ADMIN_EMAILS, else 'user'.
    """
    id_info = verify_google_token(payload.id_token)
    google_sub = id_info.get("sub")
    email = id_info.get("email")

    if not google_sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google ID token does not contain a valid subject (sub)."
        )

    # Check if user already exists
    stmt = select(User).where(User.google_sub == google_sub)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # Determine role
    is_admin = email and email.lower() in settings.admin_emails_list
    assigned_role = "admin" if is_admin else "user"

    if not user:
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            google_sub=google_sub,
            email=email,
            role=assigned_role,
            preferred_lang=payload.preferred_lang or "en"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Registered new user: {email} with role {assigned_role}")
    else:
        # Update role if email became admin, and update language
        if user.role != assigned_role:
            user.role = assigned_role
        if payload.preferred_lang:
            user.preferred_lang = payload.preferred_lang
        await db.commit()
        await db.refresh(user)

    # Issue app JWT
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
    }
    access_token = create_access_token(token_data)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role,
            preferred_lang=user.preferred_lang,
            created_at=user.created_at.isoformat() if user.created_at else None
        )
    )


@router.get("/users/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Retrieve current user profile."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        preferred_lang=current_user.preferred_lang,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None
    )


@router.get("/users/me/history", response_model=List[UserIncidentHistoryItem])
async def get_my_scan_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve user's personal scan history.
    Strict DPDP compliance: Returns anonymous metadata only (never raw text, URLs, or QR contents).
    """
    stmt = (
        select(Incident)
        .where(Incident.user_id == current_user.id)
        .order_by(Incident.created_at.desc())
        .limit(50)
    )
    result = await db.execute(stmt)
    incidents = result.scalars().all()

    return [
        UserIncidentHistoryItem(
            id=str(inc.id),
            input_type=inc.input_type,
            category=inc.category,
            risk_level=inc.risk_level,
            risk_score=inc.risk_score,
            reason_codes=inc.reason_codes or [],
            language=inc.language,
            domain_hash=inc.domain_hash,
            user_action_state=inc.user_action_state,
            created_at=inc.created_at.isoformat() if inc.created_at else ""
        )
        for inc in incidents
    ]


@router.delete("/users/me/history", status_code=status.HTTP_200_OK)
async def delete_my_scan_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Right to Erasure (DPDP Act 2023): Permanently deletes user's incident records."""
    stmt = delete(Incident).where(Incident.user_id == current_user.id)
    await db.execute(stmt)
    await db.commit()
    return {"message": "All personal incident telemetry has been permanently erased."}
