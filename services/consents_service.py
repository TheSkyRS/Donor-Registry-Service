# services/consents_service.py
from __future__ import annotations

from typing import Optional, List, Tuple
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from models import ConsentCreate, ConsentRead, ConsentUpdate
from models.enums import ConsentStatus
from db.models import ConsentORM, DonorORM


class DonorNotFoundError(Exception):
    """Raised when trying to attach a consent to a non-existent donor."""
    pass


class ConsentService:

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------
    # CREATE consent for a donor
    # ---------------------------
    def create_consent_for_donor(self, donor_id: UUID, payload: ConsentCreate) -> ConsentRead:

        donor_exists = (
            self.db.query(DonorORM)
            .filter(DonorORM.id == str(donor_id))
            .first()
        )
        if not donor_exists:
            raise DonorNotFoundError(f"Donor {donor_id} not found")

        obj = ConsentORM(
            id=str(uuid4()),
            donor_id=str(donor_id),
            scope=payload.scope,
            status=payload.status,
            signed_at=payload.signed_at,
            revoked_at=payload.revoked_at,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_read_model(obj)

    # ---------------------------
    # READ ONE
    # ---------------------------
    def get_consent(self, consent_id: UUID) -> Optional[ConsentRead]:
        obj = (
            self.db.query(ConsentORM)
            .filter(ConsentORM.id == str(consent_id))
            .first()
        )
        if not obj:
            return None
        return self._to_read_model(obj)

    # ---------------------------
    # LIST + FILTER + PAGINATION
    # ---------------------------
    def list_consents(
        self,
        *,
        donor_id: Optional[UUID] = None,
        status: Optional[ConsentStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[ConsentRead], int]:
        """
        Return (items, total)
        """
        q = self.db.query(ConsentORM)

        if donor_id is not None:
            q = q.filter(ConsentORM.donor_id == str(donor_id))

        if status is not None:
            q = q.filter(ConsentORM.status == status)

        total = q.count()
        objs = q.offset(offset).limit(limit).all()
        items = [self._to_read_model(o) for o in objs]
        return items, total

    # ---------------------------
    # UPDATE
    # ---------------------------
    def update_consent(self, consent_id: UUID, patch: ConsentUpdate) -> Optional[ConsentRead]:
        obj = (
            self.db.query(ConsentORM)
            .filter(ConsentORM.id == str(consent_id))
            .first()
        )
        if not obj:
            return None

        data = patch.model_dump(exclude_unset=True)

        if "scope" in data:
            obj.scope = data["scope"]
        if "status" in data:
            obj.status = data["status"]
        if "signed_at" in data:
            obj.signed_at = data["signed_at"]
        if "revoked_at" in data:
            obj.revoked_at = data["revoked_at"]

        self.db.commit()
        self.db.refresh(obj)
        return self._to_read_model(obj)

    # ---------------------------
    # DELETE
    # ---------------------------
    def delete_consent(self, consent_id: UUID) -> bool:
        obj = (
            self.db.query(ConsentORM)
            .filter(ConsentORM.id == str(consent_id))
            .first()
        )
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True

    # ---------------------------
    # ORM -> Pydantic
    # ---------------------------
    def _to_read_model(self, obj: ConsentORM) -> ConsentRead:
        data = {
            "id": UUID(obj.id),
            "donor_id": UUID(obj.donor_id),
            "scope": obj.scope,
            "status": obj.status,
            "signed_at": obj.signed_at,
            "revoked_at": obj.revoked_at,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return ConsentRead.model_validate(data)
