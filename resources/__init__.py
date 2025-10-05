from fastapi import APIRouter
from .health import router as health
from .donors import router as donors
from .organs import router as organs
from .consents import router as consents
from .root import router as root

api = APIRouter()
api.include_router(root)
api.include_router(health)
api.include_router(donors)
api.include_router(organs)
api.include_router(consents)