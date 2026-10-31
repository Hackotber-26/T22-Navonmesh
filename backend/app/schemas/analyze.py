from typing import List, Optional, Literal
from pydantic import BaseModel, Field


InputType = Literal["text", "url", "qr", "screenshot"]
RiskLevel = Literal["low", "medium", "high", "critical"]
UserActionState = Literal["not_acted", "clicked", "paid"]

Category = Literal[
    "UPI_COLLECT_FRAUD",
    "FAKE_KYC",
    "FAKE_BANK_LINK",
    "PARCEL_DELIVERY",
    "ELECTRICITY_BILL",
    "LOTTERY_PRIZE",
    "JOB_SCAM",
    "MALICIOUS_QR",
    "OTHER"
]


class AnalyzeRequest(BaseModel):
    input_type: InputType = Field(
        ...,
        description="Type of input: text, url, qr, or screenshot"
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Raw message text, URL string, or decoded QR payload (processed in-memory only)"
    )
    language: str = Field(
        default="en",
        description="Preferred language code: hi, bn, mr, kn, or en"
    )
    user_action_state: UserActionState = Field(
        default="not_acted",
        description="Current user state: not_acted, clicked, or paid"
    )


class AnalyzeResponse(BaseModel):
    incident_id: Optional[str] = Field(
        default=None,
        description="Anonymous incident UUID if recorded in telemetry"
    )
    risk_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Calculated risk score between 0.0 and 1.0"
    )
    risk_level: RiskLevel = Field(
        ...,
        description="Calculated risk level: low (<0.3), medium (0.3-0.6), high (0.6-0.85), critical (>=0.85)"
    )
    category: str = Field(
        ...,
        description="Primary fraud or threat category"
    )
    reason_codes: List[str] = Field(
        default_factory=list,
        description="Identified risk indicator codes"
    )
    action_codes: List[str] = Field(
        default_factory=list,
        description="Ordered action codes from the action engine"
    )
    model_version: str = Field(
        ...,
        description="Active model or detector version"
    )
    rules_version: str = Field(
        ...,
        description="Active action engine rules version"
    )
    extracted_domains: List[str] = Field(
        default_factory=list,
        description="Sanitized domain names detected (excluding full paths or user queries)"
    )

