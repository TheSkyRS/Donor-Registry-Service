# resources/organs.py
from __future__ import annotations

from uuid import UUID
from urllib.parse import urlencode

from fastapi import (
    APIRouter,
    status,
    Path,
    Query,
    Depends,
    HTTPException,
    Request,
)
from sqlalchemy.orm import Session

from models import OrganRead, OrganUpdate
from models.enums import OrganType
from services.organs_service import OrganService
from db.session import get_db

router = APIRouter(prefix="/organs", tags=["organs"])


# ----------------------
# Helper: Service
# ----------------------

def get_organ_service(db: Session = Depends(get_db)) -> OrganService:
    return OrganService(db)


# ----------------------
# Organs Collection (async)
# ----------------------

@router.get("")
async def list_organs(
    donor_id: UUID | None = Query(
        default=None,
        description="Filter by donor ID",
    ),
    organ_type: OrganType | None = Query(
        default=None,
        description="Filter by organ type",
    ),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    request: Request = ...,
    service: OrganService = Depends(get_organ_service),
):
    """
    List all organs in the registry.

    Optional filters:
    - donor_id: only organs that belong to a given donor
    - organ_type: only organs of a given type

    Includes pagination + simple linked data:
    - item._links.self   -> /organs/{id}
    - item._links.donor  -> /donors/{donor_id}
    """

    organs, total = service.list_organs(
        donor_id=donor_id,
        organ_type=organ_type,
        limit=limit,
        offset=offset,
    )

    base_path = request.url.path
    q_dict = dict(request.query_params)
    q_dict["limit"] = str(limit)

    def make_link(new_offset: int) -> str:
        q_dict_local = dict(q_dict)
        q_dict_local["offset"] = str(new_offset)
        return f"{base_path}?{urlencode(q_dict_local)}"

    envelope = {
        "items": [
            {
                "data": organ,
                "_links": {
                    "self": f"/organs/{organ.id}",
                    "donor": f"/donors/{organ.donor_id}",
                },
            }
            for organ in organs
        ],
        "count": len(organs),
        "total": total,
        "_links": {
            "self": str(request.url),
            "next": make_link(offset + limit) if offset + limit < total else None,
            "prev": make_link(max(offset - limit, 0)) if offset > 0 else None,
        },
    }
    return envelope


# ----------------------
# Organ READ ONE (async)
# ----------------------

@router.get("/{organ_id}", response_model=OrganRead)
async def get_organ(
    organ_id: UUID = Path(..., description="Organ ID"),
    service: OrganService = Depends(get_organ_service),
):
    """
    Retrieve an organ record by its ID.
    """
    organ = service.get_organ(organ_id)
    if not organ:
        raise HTTPException(status_code=404, detail="Organ not found")
    return organ


# ----------------------
# Organ UPDATE (async)
# ----------------------

@router.put("/{organ_id}", response_model=OrganRead)
async def update_organ(
    organ_id: UUID = Path(..., description="Organ ID"),
    patch: OrganUpdate = ...,
    service: OrganService = Depends(get_organ_service),
):
    """
    Update an organ record by its ID.
    """
    updated = service.update_organ(organ_id, patch)
    if not updated:
        raise HTTPException(status_code=404, detail="Organ not found")
    return updated


# ----------------------
# Organ DELETE (async)
# ----------------------

@router.delete("/{organ_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organ(
    organ_id: UUID = Path(..., description="Organ ID"),
    service: OrganService = Depends(get_organ_service),
):
    """
    Delete an organ record by its ID.
    """
    ok = service.delete_organ(organ_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Organ not found")
    return
