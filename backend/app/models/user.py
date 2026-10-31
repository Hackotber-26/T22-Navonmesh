import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.core.guid import GUID


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    google_sub = Column(String(255), unique=True, index=True, nullable=True)
    email = Column(String(255), nullable=True, index=True)
    role = Column(String(50), default="user", nullable=False)
    preferred_lang = Column(String(10), default="en", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    incidents = relationship("Incident", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")

