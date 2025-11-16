# services/donors_service.py
from __future__ import annotations

from typing import Optional, Tuple, List
from uuid import uuid4, UUID

from sqlalchemy.orm import Session
from sqlalchemy import or_

from models import DonorCreate, DonorRead, DonorUpdate
from models.enums import BloodType, CommonStatus
from db.models import DonorORM


def _split_full_name(full_name: str) -> tuple[str, str]:
    """
    "Alice Lee" -> ("Alice", "Lee")
    "Prince" -> ("Prince", "")
    """
    parts = full_name.strip().split(" ", 1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def _join_full_name(first_name: str, last_name: str) -> str:
    return f"{first_name} {last_name}".strip()


class DonorService:

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------
    # CREATE
    # ---------------------------
    def create_donor(self, payload: DonorCreate) -> DonorRead:
        first_name, last_name = _split_full_name(payload.full_name)

        obj = DonorORM(
            id=str(uuid4()),
            first_name=first_name,
            last_name=last_name,
            dob=payload.dob,
            blood_type=payload.blood_type,
            status=payload.status,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return self._to_read_model(obj)

    # ---------------------------
    # READ ONE
    # ---------------------------
    def get_donor(self, donor_id: UUID) -> Optional[DonorRead]:
        obj = (
            self.db.query(DonorORM)
            .filter(DonorORM.id == str(donor_id))
            .first()
        )
        if not obj:
            return None
        return self._to_read_model(obj)

    # ---------------------------
    # LIST + FILTER + NAME SEARCH + PAGINATION
    # ---------------------------
    def list_donors(
        self,
        *,
        blood_type: Optional[BloodType] = None,
        status: Optional[CommonStatus] = None,
        name: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[DonorRead], int]:
        q = self.db.query(DonorORM)

        if blood_type is not None:
            q = q.filter(DonorORM.blood_type == blood_type)

        if status is not None:
            q = q.filter(DonorORM.status == status)

        if name is not None and name.strip():
            pattern = f"%{name.strip()}%"
            q = q.filter(
                or_(
                    DonorORM.first_name.ilike(pattern),
                    DonorORM.last_name.ilike(pattern),
                )
            )

        total = q.count()
        objs = q.offset(offset).limit(limit).all()
        items = [self._to_read_model(o) for o in objs]
        return items, total

    # ---------------------------
    # UPDATE
    # ---------------------------
    def update_donor(self, donor_id: UUID, patch: DonorUpdate) -> Optional[DonorRead]:
        obj = (
            self.db.query(DonorORM)
            .filter(DonorORM.id == str(donor_id))
            .first()
        )
        if not obj:
            return None

        data = patch.model_dump(exclude_unset=True)

        if "full_name" in data:
            first_name, last_name = _split_full_name(data.pop("full_name"))
            obj.first_name = first_name
            obj.last_name = last_name

        if "dob" in data:
            obj.dob = data["dob"]
        if "blood_type" in data:
            obj.blood_type = data["blood_type"]
        if "status" in data:
            obj.status = data["status"]

        self.db.commit()
        self.db.refresh(obj)
        return self._to_read_model(obj)

    # ---------------------------
    # DELETE
    # ---------------------------
    def delete_donor(self, donor_id: UUID) -> bool:
        obj = (
            self.db.query(DonorORM)
            .filter(DonorORM.id == str(donor_id))
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
    def _to_read_model(self, obj: DonorORM) -> DonorRead:
        full_name = _join_full_name(obj.first_name, obj.last_name)
        data = {
            "id": UUID(obj.id),
            "full_name": full_name,
            "dob": obj.dob,
            "blood_type": obj.blood_type,
            "status": obj.status,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return DonorRead.model_validate(data)
