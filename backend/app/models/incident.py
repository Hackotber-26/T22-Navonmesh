import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index, JSON, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY as PG_ARRAY
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id = Column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    input_type = Column(String(50), nullable=False)  # text | url | qr | screenshot
    category = Column(String(100), nullable=False)
    risk_level = Column(String(50), nullable=False)  # low | medium | high | critical
    risk_score = Column(Float, nullable=False)

    # Array of strings on Postgres, JSON array on SQLite
    reason_codes = Column(PG_ARRAY(String).with_variant(JSON, "sqlite"), nullable=False, default=list)
    language = Column(String(10), nullable=False, default="en")

    # Hash of domain only (never URL or message content, for DPDP compliance)
    domain_hash = Column(String(64), nullable=True, index=True)

    # Self-reported user response state: not_acted | clicked | paid
    user_action_state = Column(String(50), nullable=True)

    actions_shown = Column(PG_ARRAY(String).with_variant(JSON, "sqlite"), nullable=False, default=list)
    model_version = Column(String(50), nullable=False)
    rules_version = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="incidents")
    reports = relationship("Report", back_populates="incident", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_incidents_created_at", "created_at"),
        Index("idx_incidents_category_risk", "category", "risk_level"),
    )
