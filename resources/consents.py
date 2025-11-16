# resources/consents.py
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

from models import ConsentRead, ConsentUpdate
from models.enums import ConsentStatus
from services.consents_service import ConsentService
from db.session import get_db

router = APIRouter(prefix="/consents", tags=["consents"])


# ----------------------
# Helper: Service
# ----------------------

def get_consent_service(db: Session = Depends(get_db)) -> ConsentService:
    return ConsentService(db)


# ----------------------
# Consents Collection (async)
# ----------------------

@router.get("")
async def list_consents(
    donor_id: UUID | None = Query(
        default=None,
        description="Filter by donor ID",
    ),
    status_q: ConsentStatus | None = Query(
        default=None,
        alias="status",
        description="Filter by consent status (granted|revoked|pending)",
    ),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    request: Request = ...,
    service: ConsentService = Depends(get_consent_service),
):
    """
    List all consents in the registry.

    Optional filters:
    - donor_id: only consents for a given donor
    - status: by consent status (granted / revoked / pending)

    Includes pagination + simple linked data:
    - item._links.self   -> /consents/{id}
    - item._links.donor  -> /donors/{donor_id}
    """

    consents, total = service.list_consents(
        donor_id=donor_id,
        status=status_q,
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
                "data": consent,
                "_links": {
                    "self": f"/consents/{consent.id}",
                    "donor": f"/donors/{consent.donor_id}",
                },
            }
            for consent in consents
        ],
        "count": len(consents),
        "total": total,
        "_links": {
            "self": str(request.url),
            "next": make_link(offset + limit) if offset + limit < total else None,
            "prev": make_link(max(offset - limit, 0)) if offset > 0 else None,
        },
    }
    return envelope


# ----------------------
# Consent READ ONE (async)
# ----------------------

@router.get("/{consent_id}", response_model=ConsentRead)
async def get_consent(
    consent_id: UUID = Path(..., description="Consent ID"),
    service: ConsentService = Depends(get_consent_service),
):
    """
    Retrieve a consent record by its ID.
    """
    consent = service.get_consent(consent_id)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
    return consent


# ----------------------
# Consent UPDATE (async)
# ----------------------

@router.put("/{consent_id}", response_model=ConsentRead)
async def update_consent(
    consent_id: UUID = Path(..., description="Consent ID"),
    patch: ConsentUpdate = ...,
    service: ConsentService = Depends(get_consent_service),
):
    """
    Update a consent record by its ID.
    """
    updated = service.update_consent(consent_id, patch)
    if not updated:
        raise HTTPException(status_code=404, detail="Consent not found")
    return updated


# ----------------------
# Consent DELETE (async)
# ----------------------

@router.delete("/{consent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consent(
    consent_id: UUID = Path(..., description="Consent ID"),
    service: ConsentService = Depends(get_consent_service),
):
    """
    Delete a consent record by its ID.
    """
    ok = service.delete_consent(consent_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Consent not found")
    return
