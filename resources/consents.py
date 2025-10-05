# resources/consents.py
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, status, Path, Query
from models import ConsentRead, ConsentUpdate
from utils.responses import not_implemented

router = APIRouter(prefix="/consents", tags=["consents"])


@router.get("", response_model=list[ConsentRead])
def list_consents(
    donor_id: UUID | None = Query(default=None, description="Filter by donor ID"),
    status_q: str | None = Query(default=None, alias="status", description="Filter by consent status (granted|revoked|pending)"),
):
    """
    List all consent records.

    Optionally filter by donor ID or status.
    Example: GET /consents?donor_id=uuid&status=granted
    """
    return not_implemented()


@router.get("/{consent_id}", response_model=ConsentRead)
def get_consent(consent_id: UUID = Path(..., description="Consent ID")):
    """
    Retrieve a consent record by its ID.
    """
    return not_implemented()


@router.put("/{consent_id}", response_model=ConsentRead)
def update_consent(
    consent_id: UUID = Path(..., description="Consent ID"),
    patch: ConsentUpdate = ...,
):
    """
    Update a consent record by its ID.
    """
    return not_implemented()


@router.delete("/{consent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_consent(consent_id: UUID = Path(..., description="Consent ID")):
    """
    Delete a consent record by its ID.
    """
    return not_implemented()