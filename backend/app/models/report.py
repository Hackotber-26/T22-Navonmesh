import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        primary_key=True,
        default=uuid.uuid4
    )
    incident_id = Column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        PG_UUID(as_uuid=True).with_variant(String(36), "sqlite"),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    verdict = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    incident = relationship("Incident", back_populates="reports")
    user = relationship("User", back_populates="reports")

    __table_args__ = (
        Index("idx_reports_created_at", "created_at"),
    )
