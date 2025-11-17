# models/consent.py
from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import BaseModel, Field

from .enums import ConsentStatus, OrganType


class ConsentBase(BaseModel):
    """
    Shared fields for Consent models.
    Represents a donor's authorization to donate organs (scope + status).
    """
    scope: list[OrganType] = Field(
        ...,
        min_length=1,
        description="List of organs the donor authorizes for donation (must contain at least one organ).",
        json_schema_extra={"example": ["kidney", "liver"]},
    )
    status: ConsentStatus = Field(
        default=ConsentStatus.PENDING,
        description="Current consent status.",
        json_schema_extra={"example": "pending"},
    )
    signed_at: Optional[datetime] = Field(
        None,
        description="UTC timestamp when the consent was signed (if signed).",
        json_schema_extra={"example": "2025-02-10T09:15:00Z"},
    )
    revoked_at: Optional[datetime] = Field(
        None,
        description="UTC timestamp when the consent was revoked (if revoked).",
        json_schema_extra={"example": "2025-03-01T12:00:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "scope": ["kidney", "liver"],
                    "status": "granted",
                    "signed_at": "2025-02-10T09:15:00Z",
                    "revoked_at": None,
                }
            ]
        }
    }


class ConsentCreate(ConsentBase):
    """
    Creation payload for a Consent.
    Note: `donor_id` is taken from the URL path when using
    POST /donors/{donor_id}/consents and is not part of the body.
    """
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "scope": ["kidney", "liver"],
                    "status": "pending",
                    "signed_at": None,
                    "revoked_at": None,
                }
            ]
        }
    }


class ConsentUpdate(BaseModel):
    """
    Partial update payload; Consent ID comes from the path.
    All fields are optional.
    """
    scope: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description='Consent scope, e.g. "all organs" or a specific list.',
        json_schema_extra={"example": "kidney, liver"},
    )
    status: Optional[ConsentStatus] = Field(
        None,
        description="Current consent status.",
        json_schema_extra={"example": "granted"},
    )
    signed_at: Optional[datetime] = Field(
        None,
        description="UTC timestamp when the consent was signed.",
        json_schema_extra={"example": "2025-02-10T09:15:00Z"},
    )
    revoked_at: Optional[datetime] = Field(
        None,
        description="UTC timestamp when the consent was revoked.",
        json_schema_extra={"example": "2025-03-01T12:00:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"status": "granted", "signed_at": "2025-02-10T09:15:00Z"},
                {"status": "revoked", "revoked_at": "2025-03-01T12:00:00Z"},
                {"scope": ["kidney", "liver"]},
            ]
        }
    }


class ConsentRead(ConsentBase):
    """
    Read model returned by the API.
    Includes immutable identifiers and server-managed timestamps.
    """
    id: UUID = Field(
        default_factory=uuid4,
        description="Persistent Consent ID (server-generated).",
        json_schema_extra={"example": "2a4b01f7-5f5e-4a0a-8e0c-1a2b3c4d5e6f"},
    )
    donor_id: UUID = Field(
        ...,
        description="ID of the Donor this consent belongs to.",
        json_schema_extra={"example": "7f1d69a7-b8d2-4e75-9c1c-6f1e6b2a9d77"},
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-02-10T09:00:00Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-02-10T09:20:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "2a4b01f7-5f5e-4a0a-8e0c-1a2b3c4d5e6f",
                    "donor_id": "7f1d69a7-b8d2-4e75-9c1c-6f1e6b2a9d77",
                    "scope": ["kidney", "liver"],
                    "status": "granted",
                    "signed_at": "2025-02-10T09:15:00Z",
                    "revoked_at": None,
                    "created_at": "2025-02-10T09:00:00Z",
                    "updated_at": "2025-02-10T09:20:00Z",
                }
            ]
        }
    }