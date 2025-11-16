from __future__ import annotations

from framework.app_factory import create_app

app = create_app()

# -----------------------------------------------------------------------------
# Entrypoint for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    import os

    from db.base import Base, engine
    # for test, automatically create table (if not exists)
    Base.metadata.create_all(bind=engine)
    port = int(os.environ.get("PORT", 8080))  # Cloud Run uses PORT
    uvicorn.run("main:app", host="0.0.0.0", port=port)