# services/organs_service.py
from __future__ import annotations

from typing import Optional, List, Tuple
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from models import OrganCreate, OrganRead, OrganUpdate
from models.enums import OrganType
from db.models import OrganORM, DonorORM


class DonorNotFoundError(Exception):
    """Raised when trying to attach an organ to a non-existent donor."""
    pass


class OrganService:

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------
    # CREATE organ for a donor
    # ---------------------------
    def create_organ_for_donor(self, donor_id: UUID, payload: OrganCreate) -> OrganRead:

        donor_exists = (
            self.db.query(DonorORM)
            .filter(DonorORM.id == str(donor_id))
            .first()
        )
        if not donor_exists:
            raise DonorNotFoundError(f"Donor {donor_id} not found")

        obj = OrganORM(
            id=str(uuid4()),
            donor_id=str(donor_id),
            organ_type=payload.organ_type,
            condition=payload.condition,
            retrieved_at=payload.retrieved_at,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_read_model(obj)

    # ---------------------------
    # READ ONE
    # ---------------------------
    def get_organ(self, organ_id: UUID) -> Optional[OrganRead]:
        obj = (
            self.db.query(OrganORM)
            .filter(OrganORM.id == str(organ_id))
            .first()
        )
        if not obj:
            return None
        return self._to_read_model(obj)

    # ---------------------------
    # LIST + FILTER + PAGINATION
    # ---------------------------
    def list_organs(
        self,
        *,
        donor_id: Optional[UUID] = None,
        organ_type: Optional[OrganType] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[OrganRead], int]:
        """
        Return (items, total)
        """
        q = self.db.query(OrganORM)

        if donor_id is not None:
            q = q.filter(OrganORM.donor_id == str(donor_id))

        if organ_type is not None:
            q = q.filter(OrganORM.organ_type == organ_type)

        total = q.count()
        objs = q.offset(offset).limit(limit).all()
        items = [self._to_read_model(o) for o in objs]
        return items, total

    # ---------------------------
    # UPDATE
    # ---------------------------
    def update_organ(self, organ_id: UUID, patch: OrganUpdate) -> Optional[OrganRead]:
        obj = (
            self.db.query(OrganORM)
            .filter(OrganORM.id == str(organ_id))
            .first()
        )
        if not obj:
            return None

        data = patch.model_dump(exclude_unset=True)

        if "organ_type" in data:
            obj.organ_type = data["organ_type"]
        if "condition" in data:
            obj.condition = data["condition"]
        if "retrieved_at" in data:
            obj.retrieved_at = data["retrieved_at"]

        self.db.commit()
        self.db.refresh(obj)
        return self._to_read_model(obj)

    # ---------------------------
    # DELETE
    # ---------------------------
    def delete_organ(self, organ_id: UUID) -> bool:
        obj = (
            self.db.query(OrganORM)
            .filter(OrganORM.id == str(organ_id))
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
    def _to_read_model(self, obj: OrganORM) -> OrganRead:
        data = {
            "id": UUID(obj.id),
            "donor_id": UUID(obj.donor_id),
            "organ_type": obj.organ_type,
            "condition": obj.condition,
            "retrieved_at": obj.retrieved_at,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return OrganRead.model_validate(data)
