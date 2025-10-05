from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Donor Registry Service API — see /docs"}