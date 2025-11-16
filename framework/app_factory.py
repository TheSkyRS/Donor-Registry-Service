from __future__ import annotations

from fastapi import FastAPI
from resources import api

def create_app() -> FastAPI:
    app =  FastAPI(
        title="Donor Registry Service",
        description="Microservice 1 (Sprint 2) — Donor, Organ, Consent",
        version="0.2.0",
    )
    app.include_router(api)

    # may add some middlewares
    
    return app