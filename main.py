from __future__ import annotations

from framework.app_factory import create_app

app = create_app()

# -----------------------------------------------------------------------------
# Entrypoint for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("FASTAPIPORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)