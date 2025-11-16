# resources/donors.py
from __future__ import annotations

from uuid import UUID
import hashlib
from urllib.parse import urlencode

from fastapi import (
    APIRouter,
    status,
    Query,
    Path,
    Depends,
    HTTPException,
    Header,
    Response,
    Request,
)
from sqlalchemy.orm import Session

from models import (
    DonorCreate,
    DonorRead,
    DonorUpdate,
    OrganCreate,
    OrganRead,
    ConsentCreate,
    ConsentRead,
)
from models.enums import BloodType, CommonStatus
from services.donors_service import DonorService
from db.session import get_db

from services.organs_service import OrganService, DonorNotFoundError as OrganDonorNotFoundError
from services.consents_service import ConsentService, DonorNotFoundError as ConsentDonorNotFoundError

router = APIRouter(prefix="/donors", tags=["donors"])


# ----------------------
# Helper: Service + ETag
# ----------------------

def get_donor_service(db: Session = Depends(get_db)) -> DonorService:
    return DonorService(db)

def get_organ_service(db: Session = Depends(get_db)) -> OrganService:
    return OrganService(db)

def get_consent_service(db: Session = Depends(get_db)) -> ConsentService:
    return ConsentService(db)


def make_etag(donor: DonorRead) -> str:
    """
    use donor.id + donor.updated_at to generate 'weak' ETag
    """
    raw = f"{donor.id}:{donor.updated_at.isoformat()}".encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    return f'W/"{digest}"'


# ----------------------
# Donor Collection (async)
# ----------------------

@router.get("")
async def list_donors(
    blood_type: BloodType | None = Query(default=None),
    status_q: CommonStatus | None = Query(default=None, alias="status"),
    name: str | None = Query(
        default=None,
        description="Case-insensitive substring match on first or last name",
    ),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    request: Request = ...,
    service: DonorService = Depends(get_donor_service),
):
    """
    List donors with optional filters:
    - blood_type
    - status
    - name (substring search on first/last name)
    Includes pagination + HATEOAS-style links.

    linked data : organs/consents use
      /organs?donor_id=... and /consents?donor_id=...
    instead of /donors/{id}/organs this kind of relative path.
    """
    donors, total = service.list_donors(
        blood_type=blood_type,
        status=status_q,
        name=name,
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
                "data": donor,
                "_links": {
                    "self": f"/donors/{donor.id}",
                    "organs": f"/organs?donor_id={donor.id}",
                    "consents": f"/consents?donor_id={donor.id}",
                },
            }
            for donor in donors
        ],
        "count": len(donors),
        "total": total,
        "_links": {
            "self": str(request.url),
            "next": make_link(offset + limit) if offset + limit < total else None,
            "prev": make_link(max(offset - limit, 0)) if offset > 0 else None,
        },
    }
    return envelope


# ----------------------
# Donor CREATE (async)
# ----------------------

@router.post("", response_model=DonorRead, status_code=status.HTTP_201_CREATED)
async def create_donor(
    d: DonorCreate,
    response: Response,
    service: DonorService = Depends(get_donor_service),
):
    """
    Create a new donor.
    Returns 201 + Location header + ETag.
    """
    created = service.create_donor(d)

    response.headers["Location"] = f"/donors/{created.id}"
    response.headers["ETag"] = make_etag(created)
    return created


# ----------------------
# Donor READ ONE (async, with ETag / If-None-Match)
# ----------------------

@router.get("/{donor_id}", response_model=DonorRead)
async def get_donor(
    donor_id: UUID = Path(...),
    response: Response = ...,
    if_none_match: str | None = Header(default=None, alias="If-None-Match"),
    service: DonorService = Depends(get_donor_service),
):
    """
    Retrieve a single donor by ID.
    Supports ETag / If-None-Match → 304 Not Modified.
    """
    donor = service.get_donor(donor_id)
    if not donor:
        raise HTTPException(status_code=404, detail="Donor not found")

    etag = make_etag(donor)

    if if_none_match == etag:
        return Response(
            status_code=status.HTTP_304_NOT_MODIFIED,
            headers={"ETag": etag},
        )
    response.headers["ETag"] = etag
    return donor


# ----------------------
# Donor UPDATE (async, with ETag / If-Match)
# ----------------------

@router.put("/{donor_id}", response_model=DonorRead)
async def update_donor(
    donor_id: UUID,
    patch: DonorUpdate,
    response: Response,
    if_match: str | None = Header(default=None, alias="If-Match"),
    service: DonorService = Depends(get_donor_service),
):
    """
    Update a donor record by ID.
    Requires If-Match ETag for optimistic locking.
    """
    # Etag validation
    current = service.get_donor(donor_id)
    if not current:
        raise HTTPException(status_code=404, detail="Donor not found")

    current_etag = make_etag(current)

    if if_match is None or if_match != current_etag:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="ETag mismatch or missing If-Match header",
        )

    updated = service.update_donor(donor_id, patch)
    new_etag = make_etag(updated)
    response.headers["ETag"] = new_etag
    return updated


# ----------------------
# Donor DELETE (async)
# ----------------------

@router.delete("/{donor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_donor(
    donor_id: UUID,
    service: DonorService = Depends(get_donor_service),
):
    """
    Delete a donor record by ID.
    """
    ok = service.delete_donor(donor_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Donor not found")
    return


# ----------------------
# Organs (subresource views)
# ----------------------

@router.get("/{donor_id}/organs", response_model=list[OrganRead])
async def list_organs_for_donor(
    donor_id: UUID = Path(...),
    service: OrganService = Depends(get_organ_service),
):
    """
    List all organs belonging to a specific donor.

    No pagination.
    """
    organs, _total = service.list_organs(
        donor_id=donor_id,
        limit=1000,
        offset=0,
    )
    return organs


@router.post(
    "/{donor_id}/organs",
    response_model=OrganRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_organ_for_donor(
    donor_id: UUID,
    o: OrganCreate,
    service: OrganService = Depends(get_organ_service),
):
    """
    Create a new organ record for a specific donor.
    """
    try:
        created = service.create_organ_for_donor(donor_id, o)
    except OrganDonorNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Donor {donor_id} not found",
        )
    return created


# ----------------------
# Consents (subresource views)
# ----------------------

@router.get("/{donor_id}/consents", response_model=list[ConsentRead])
async def list_consents_for_donor(
    donor_id: UUID = Path(...),
    service: ConsentService = Depends(get_consent_service),
):
    """
    List all consent records for a specific donor.
    """
    consents, _total = service.list_consents(
        donor_id=donor_id,
        limit=1000,
        offset=0,
    )
    return consents


@router.post(
    "/{donor_id}/consents",
    response_model=ConsentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_consent_for_donor(
    donor_id: UUID,
    c: ConsentCreate,
    service: ConsentService = Depends(get_consent_service),
):
    """
    Create a new consent record for a donor.
    """
    try:
        created = service.create_consent_for_donor(donor_id, c)
    except ConsentDonorNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Donor {donor_id} not found",
        )
    return created

