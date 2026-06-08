"""ACE — Autonomous Coding Engine API entrypoint."""
from __future__ import annotations

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from .config import settings
from .db import engine
from .llm.client import LLMUnavailable
from .routes import cdi, coding, encounters, insights, meta, ops
from .seed.seeder import seed_all


def _wait_for_db(retries: int = 30, delay: float = 2.0) -> None:
    for attempt in range(retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)


def create_app() -> FastAPI:
    app = FastAPI(title="ACE — Autonomous Coding Engine", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(LLMUnavailable)
    async def _llm_unavailable(_: Request, exc: LLMUnavailable):
        return JSONResponse(status_code=503, content={"error": "llm_unavailable", "detail": str(exc)})

    for r in (meta.router, encounters.router, coding.router, insights.router, cdi.router, ops.router):
        app.include_router(r, prefix="/api")

    @app.on_event("startup")
    def _startup() -> None:
        _wait_for_db()
        if settings.ace_auto_seed:
            result = seed_all()
            print(f"[seed] {result}", flush=True)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    _wait_for_db()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
