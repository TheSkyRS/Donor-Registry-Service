# models/donor.py
from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4
from datetime import date, datetime

from pydantic import BaseModel, Field

from .enums import BloodType, CommonStatus


class DonorBase(BaseModel):
    """
    Shared fields for Donor models.
    """
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Donor's legal full name.",
        json_schema_extra={"example": "Alice Lee"},
    )
    dob: date = Field(
        ...,
        description="Date of birth (YYYY-MM-DD).",
        json_schema_extra={"example": "1990-05-10"},
    )
    blood_type: BloodType = Field(
        ...,
        description="ABO/Rh blood type.",
        json_schema_extra={"example": "O+"},
    )
    status: CommonStatus = Field(
        default=CommonStatus.ACTIVE,
        description="Donor profile status (active/inactive).",
        json_schema_extra={"example": "active"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "full_name": "Alice Lee",
                    "dob": "1990-05-10",
                    "blood_type": "O+",
                    "status": "active",
                }
            ]
        }
    }


class DonorCreate(DonorBase):
    """
    Creation payload.
    Server generates `id`, `created_at`, and `updated_at`.
    """
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "full_name": "Bob Chen",
                    "dob": "1985-02-14",
                    "blood_type": "A-",
                    "status": "active",
                }
            ]
        }
    }


class DonorUpdate(BaseModel):
    """
    Partial update payload; Donor ID comes from the path, not the body.
    All fields are optional.
    """
    full_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Donor's legal full name.",
        json_schema_extra={"example": "Robert Chen"},
    )
    dob: Optional[date] = Field(
        None,
        description="Date of birth (YYYY-MM-DD).",
        json_schema_extra={"example": "1985-02-14"},
    )
    blood_type: Optional[BloodType] = Field(
        None,
        description="ABO/Rh blood type.",
        json_schema_extra={"example": "A-"},
    )
    status: Optional[CommonStatus] = Field(
        None,
        description="Donor profile status (active/inactive).",
        json_schema_extra={"example": "inactive"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"full_name": "Robert Chen"},
                {"status": "inactive"},
                {"blood_type": "B+"},
            ]
        }
    }


class DonorRead(DonorBase):
    """
    Read model returned by the API.
    Includes server-managed identifiers and timestamps.
    """
    id: UUID = Field(
        default_factory=uuid4,
        description="Persistent Donor ID (server-generated).",
        json_schema_extra={"example": "7f1d69a7-b8d2-4e75-9c1c-6f1e6b2a9d77"},
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-01-15T10:20:30Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-01-16T12:00:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "7f1d69a7-b8d2-4e75-9c1c-6f1e6b2a9d77",
                    "full_name": "Alice Lee",
                    "dob": "1990-05-10",
                    "blood_type": "O+",
                    "status": "active",
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z",
                }
            ]
        }
    }