# resources/organs.py
from __future__ import annotations

from uuid import UUID
from fastapi import APIRouter, status, Path, Query
from models import OrganRead, OrganUpdate
from utils.responses import not_implemented

router = APIRouter(prefix="/organs", tags=["organs"])

@router.get("", response_model=list[OrganRead])
def list_organs(
    donor_id: UUID | None = Query(default=None, description="Filter by donor ID"),
    organ_type: str | None = Query(default=None, description="Filter by organ type"),
):
    """
    List all organs in the registry.

    Optionally filter by donor ID or organ type.
    Example: GET /organs?donor_id=uuid&organ_type=kidney
    """
    return not_implemented()


@router.get("/{organ_id}", response_model=OrganRead)
def get_organ(organ_id: UUID = Path(..., description="Organ ID")):
    """
    Retrieve an organ record by its ID.
    """
    return not_implemented()


@router.put("/{organ_id}", response_model=OrganRead)
def update_organ(
    organ_id: UUID = Path(..., description="Organ ID"),
    patch: OrganUpdate = ...,
):
    """
    Update an organ record by its ID.
    """
    return not_implemented()


@router.delete("/{organ_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organ(organ_id: UUID = Path(..., description="Organ ID")):
    """
    Delete an organ record by its ID.
    """
    return not_implemented()