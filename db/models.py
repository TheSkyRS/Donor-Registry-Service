# SQLAlchemy ORM models (DonorORM, OrganORM, ConsentORM)
# db/models.py
from sqlalchemy import (
    Column,
    String,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime

from db.base import Base
from models.enums import BloodType, CommonStatus, OrganType, ConsentStatus


# ============================================================
# Donor ORM (first_name + last_name)
# ============================================================

class DonorORM(Base):
    __tablename__ = "donors"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))

    # full_name.split() (need to convert)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    dob = Column(Date, nullable=False)
    blood_type = Column(Enum(BloodType), nullable=False)
    status = Column(Enum(CommonStatus), nullable=False, default=CommonStatus.ACTIVE)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ORM relationships
    organs = relationship("OrganORM", back_populates="donor", cascade="all, delete-orphan")
    consents = relationship("ConsentORM", back_populates="donor", cascade="all, delete-orphan")


# ============================================================
# Organ ORM
# ============================================================

class OrganORM(Base):
    __tablename__ = "organs"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))
    donor_id = Column(CHAR(36), ForeignKey("donors.id"), nullable=False)

    organ_type = Column(Enum(OrganType), nullable=False)
    condition = Column(String(100), nullable=False)
    retrieved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    donor = relationship("DonorORM", back_populates="organs")


# ============================================================
# Consent ORM
# ============================================================

class ConsentORM(Base):
    __tablename__ = "consents"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid4()))
    donor_id = Column(CHAR(36), ForeignKey("donors.id"), nullable=False)

    scope = Column(String(200), nullable=False)
    status = Column(Enum(ConsentStatus), nullable=False, default=ConsentStatus.PENDING)
    signed_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    donor = relationship("DonorORM", back_populates="consents")
