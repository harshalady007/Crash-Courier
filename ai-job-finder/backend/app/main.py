"""AI Job Finder — FastAPI application entry point.

Run: uvicorn app.main:app --reload
Docs: /docs (Swagger UI) · Architecture: ../docs/02-system-architecture.md
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .connectors import build_connectors
from .database import init_db
from .routers import automation, jobs, resumes
from .services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # In-process scheduler only makes sense on a long-lived server; on serverless
    # (Vercel) use platform cron hitting /api/automation/schedules/{id}/run instead.
    if not os.environ.get("VERCEL"):
        start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title=settings.app_name, version=settings.version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resumes.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(automation.router, prefix="/api")


@app.get("/api/health")
def health():
    connectors = build_connectors(settings)
    return {
        "status": "ok",
        "version": settings.version,
        "connectors_enabled": [c.id for c in connectors if c.enabled],
        "llm_configured": bool(settings.anthropic_api_key),
    }
