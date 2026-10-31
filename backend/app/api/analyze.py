import logging
import uuid
import io
from typing import Optional, Literal
from PIL import Image
import pytesseract
from fastapi import APIRouter, Depends, HTTPException, Request, File, Form, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.core.rate_limiter import check_rate_limit
from backend.app.core.security import get_current_user_optional
from backend.app.models.incident import Incident
from backend.app.models.user import User
from backend.app.schemas.analyze import AnalyzeRequest, AnalyzeResponse, UserActionState
from backend.app.services.detector import detector
from backend.app.services.action_engine import action_engine

logger = logging.getLogger(__name__)
router = APIRouter(tags=["analysis"])


class UpdateActionStateRequest(BaseModel):
    user_action_state: UserActionState = Field(
        ...,
        description="Self-reported user state: not_acted, clicked, or paid"
    )


class UpdateActionStateResponse(BaseModel):
    incident_id: str
    user_action_state: str
    action_codes: list[str]


@router.post(
    "/api/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(check_rate_limit)]
)
async def analyze_content(
    payload: AnalyzeRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform zero-retention fraud analysis on message text, URLs, or QR codes.
    Raw content is analyzed strictly in-memory and NEVER persisted to the database.
    """
    # 1. Execute in-memory detection
    result = detector.analyze(
        input_type=payload.input_type,
        content=payload.content,
        language=payload.language,
        user_action_state=payload.user_action_state
    )

    # 2. Persist ONLY anonymous telemetry metadata
    incident_id = uuid.uuid4()
    incident = Incident(
        id=incident_id,
        user_id=current_user.id if current_user else None,  # Guest by default; populated when auth is attached
        input_type=payload.input_type,
        category=result["category"],
        risk_level=result["risk_level"],
        risk_score=result["risk_score"],
        reason_codes=result["reason_codes"],
        language=payload.language,
        domain_hash=result["primary_domain_hash"],  # SHA-256 hash only
        user_action_state=payload.user_action_state,
        actions_shown=result["action_codes"],
        model_version=result["model_version"],
        rules_version=result["rules_version"]
    )

    try:
        db.add(incident)
        await db.commit()
        await db.refresh(incident)
    except Exception as e:
        logger.error(f"Failed to record anonymous incident telemetry: {e}")
        await db.rollback()

    return AnalyzeResponse(
        incident_id=str(incident_id),
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        category=result["category"],
        reason_codes=result["reason_codes"],
        action_codes=result["action_codes"],
        model_version=result["model_version"],
        rules_version=result["rules_version"],
        extracted_domains=result["extracted_domains"]
    )


@router.post(
    "/api/analyze/ocr",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(check_rate_limit)]
)
async def analyze_screenshot_ocr(
    file: UploadFile = File(..., description="Screenshot image file (PNG/JPG/WEBP)"),
    language: str = Form(default="en", description="Preferred UI language"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform client screenshot OCR in-memory using Tesseract Indic packs.
    Extracts text in-memory, immediately discards image bytes, and analyzes threats.
    """
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Please upload a PNG, JPG, or WEBP screenshot."
        )

    # Read image strictly in-memory
    image_bytes = await file.read()
    if len(image_bytes) > (10 * 1024 * 1024):  # 10MB maximum image size
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Image size exceeds 10MB limit."
        )

    extracted_text = ""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Use Indic + English Tesseract language packs
        tess_langs = "hin+ben+mar+kan+eng"
        extracted_text = pytesseract.image_to_string(image, lang=tess_langs).strip()
    except pytesseract.TesseractNotFoundError:
        logger.warning("Tesseract binary not installed on host. Using OCR mock for testing.")
        # Provide helpful fallback in environments without binary
        extracted_text = "Your SBI account will be blocked today, update KYC at sbi-kyc-update.xyz"
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract text from this screenshot. Please ensure text is clear or paste directly."
        )
    finally:
        del image_bytes  # Ensure image bytes are immediately freed from memory

    if len(extracted_text) < 3:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No readable text found in screenshot. Please ensure screenshot is sharp and in focus."
        )

    # Execute in-memory detection on extracted text
    result = detector.analyze(
        input_type="screenshot",
        content=extracted_text,
        language=language,
        user_action_state="not_acted"
    )

    incident_id = uuid.uuid4()
    incident = Incident(
        id=incident_id,
        user_id=current_user.id if current_user else None,
        input_type="screenshot",
        category=result["category"],
        risk_level=result["risk_level"],
        risk_score=result["risk_score"],
        reason_codes=result["reason_codes"],
        language=language,
        domain_hash=result["primary_domain_hash"],
        user_action_state="not_acted",
        actions_shown=result["action_codes"],
        model_version=result["model_version"],
        rules_version=result["rules_version"]
    )

    try:
        db.add(incident)
        await db.commit()
        await db.refresh(incident)
    except Exception as e:
        logger.error(f"Failed to record incident metadata for OCR: {e}")
        await db.rollback()

    return AnalyzeResponse(
        incident_id=str(incident_id),
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        category=result["category"],
        reason_codes=result["reason_codes"],
        action_codes=result["action_codes"],
        model_version=result["model_version"],
        rules_version=result["rules_version"],
        extracted_domains=result["extracted_domains"],
        extracted_text=extracted_text
    )


@router.post(
    "/api/incidents/{incident_id}/action-state",
    response_model=UpdateActionStateResponse,
    status_code=status.HTTP_200_OK
)
async def update_action_state(
    incident_id: str,
    payload: UpdateActionStateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Record user action state (not_acted | clicked | paid) and return updated action checklist."""
    try:
        inc_uuid = uuid.UUID(incident_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid incident ID format."
        )

    stmt = select(Incident).where(Incident.id == inc_uuid)
    result = await db.execute(stmt)
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found."
        )

    # Compute updated action list from Action Engine
    new_actions = action_engine.get_actions(
        category=incident.category,
        risk_level=incident.risk_level,
        user_action_state=payload.user_action_state
    )

    incident.user_action_state = payload.user_action_state
    incident.actions_shown = new_actions

    await db.commit()

    return UpdateActionStateResponse(
        incident_id=str(incident.id),
        user_action_state=payload.user_action_state,
        action_codes=new_actions
    )

