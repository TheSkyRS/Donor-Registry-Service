# resources/donors.py
from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, status, Query, Path
from fastapi.responses import JSONResponse
from models import (
    DonorCreate,
    DonorRead,
    DonorUpdate,
    OrganCreate,
    OrganRead,
    ConsentCreate,
    ConsentRead,
)
from utils.responses import not_implemented

router = APIRouter(prefix="/donors", tags=["donors"])

# ----------------------
# Donor CRUD
# ----------------------

@router.get("", response_model=list[DonorRead])
def list_donors(
    blood_type: str | None = Query(default=None),
    status_q: str | None = Query(default=None, alias="status")
):
    """List all donors, optionally filtered by blood type or status."""
    return not_implemented()


@router.post("", response_model=DonorRead, status_code=status.HTTP_201_CREATED)
def create_donor(d: DonorCreate):
    """Create a new donor record."""
    return not_implemented()


@router.get("/{donor_id}", response_model=DonorRead)
def get_donor(donor_id: UUID = Path(...)):
    """Retrieve a single donor by ID."""
    return not_implemented()


@router.put("/{donor_id}", response_model=DonorRead)
def update_donor(donor_id: UUID, patch: DonorUpdate):
    """Update a donor record by ID."""
    return not_implemented()


@router.delete("/{donor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_donor(donor_id: UUID):
    """Delete a donor record by ID."""
    return not_implemented()


# ----------------------
# Organs (subresource)
# ----------------------

@router.get("/{donor_id}/organs", response_model=list[OrganRead])
def list_organs_for_donor(donor_id: UUID = Path(...)):
    """List all organs belonging to a specific donor."""
    return not_implemented()


@router.post("/{donor_id}/organs", response_model=OrganRead, status_code=status.HTTP_201_CREATED)
def create_organ_for_donor(donor_id: UUID, o: OrganCreate):
    """Create a new organ record for a specific donor."""
    return not_implemented()

# ----------------------
# Consents (subresource)
# ----------------------

@router.get("/{donor_id}/consents", response_model=list[ConsentRead])
def list_consents_for_donor(donor_id: UUID = Path(...)):
    """List all consent records for a specific donor."""
    return not_implemented()


@router.post("/{donor_id}/consents", response_model=ConsentRead, status_code=status.HTTP_201_CREATED)
def create_consent_for_donor(donor_id: UUID, c: ConsentCreate):
    """Create a new consent record for a donor."""
    return not_implemented()
