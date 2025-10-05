# models/organ.py
from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import BaseModel, Field

from .enums import OrganType


class OrganBase(BaseModel):
    """
    Shared fields for Organ models.
    """
    organ_type: OrganType = Field(
        ...,
        description="Type of the organ available for donation.",
        json_schema_extra={"example": "kidney"},
    )
    condition: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Brief assessment of organ condition at retrieval/intake.",
        json_schema_extra={"example": "viable"},
    )
    retrieved_at: Optional[datetime] = Field(
        None,
        description="UTC timestamp when the organ was retrieved (if known).",
        json_schema_extra={"example": "2025-01-15T08:30:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "organ_type": "kidney",
                    "condition": "viable",
                    "retrieved_at": "2025-01-15T08:30:00Z",
                }
            ]
        }
    }


class OrganCreate(OrganBase):
    """
    Creation payload for an Organ.
    Note: `donor_id` comes from the URL path when using
    POST /donors/{donor_id}/organs and is not part of the body.
    """
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "organ_type": "heart",
                    "condition": "good",
                    "retrieved_at": "2025-02-01T14:05:00Z",
                }
            ]
        }
    }


class OrganUpdate(BaseModel):
    """
    Partial update payload; Organ ID is taken from the path.
    All fields are optional.
    """
    organ_type: Optional[OrganType] = Field(
        None,
        description="Type of the organ.",
        json_schema_extra={"example": "liver"},
    )
    condition: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Brief assessment of organ condition.",
        json_schema_extra={"example": "fair"},
    )
    retrieved_at: Optional[datetime] = Field(
        None,
        description="UTC timestamp when the organ was retrieved.",
        json_schema_extra={"example": "2025-02-02T10:00:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"condition": "excellent"},
                {"organ_type": "lung"},
                {"retrieved_at": "2025-02-02T10:00:00Z"},
            ]
        }
    }


class OrganRead(OrganBase):
    """
    Read model returned by the API.
    Includes immutable identifiers and server-managed timestamps.
    """
    id: UUID = Field(
        default_factory=uuid4,
        description="Persistent Organ ID (server-generated).",
        json_schema_extra={"example": "3a7f4c9e-5f0a-44f6-9f7e-1d2b3c4d5e6f"},
    )
    donor_id: UUID = Field(
        ...,
        description="ID of the Donor this organ belongs to.",
        json_schema_extra={"example": "7f1d69a7-b8d2-4e75-9c1c-6f1e6b2a9d77"},
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-02-01T14:10:00Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-02-01T15:45:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "3a7f4c9e-5f0a-44f6-9f7e-1d2b3c4d5e6f",
                    "donor_id": "7f1d69a7-b8d2-4e75-9c1c-6f1e6b2a9d77",
                    "organ_type": "kidney",
                    "condition": "viable",
                    "retrieved_at": "2025-01-15T08:30:00Z",
                    "created_at": "2025-02-01T14:10:00Z",
                    "updated_at": "2025-02-01T15:45:00Z",
                }
            ]
        }
    }