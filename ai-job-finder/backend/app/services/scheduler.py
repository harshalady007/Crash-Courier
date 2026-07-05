"""Daily automation: re-run saved searches, optionally email a digest.

MVP uses an in-process APScheduler job (fires daily). Production should move this to a
platform cron hitting POST /api/automation/schedules/{id}/run — see docs/08.
"""
from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from ..config import get_settings
from ..database import SessionLocal
from ..models import JobMatch, Resume, SavedSearch
from .search_service import run_search

logger = logging.getLogger(__name__)
_scheduler: AsyncIOScheduler | None = None


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(run_all_saved_searches, "cron", hour=7, minute=0, id="daily-saved-searches")
    _scheduler.start()
    logger.info("scheduler started (daily saved searches at 07:00)")


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None


async def run_all_saved_searches() -> None:
    db = SessionLocal()
    try:
        searches = db.scalars(select(SavedSearch).where(SavedSearch.active.is_(True))).all()
        for saved in searches:
            try:
                await run_saved_search(db, saved)
            except Exception:  # noqa: BLE001 — one failing schedule must not stop the rest
                logger.exception("saved search %s failed", saved.id)
    finally:
        db.close()


async def run_saved_search(db, saved: SavedSearch) -> dict:
    resume = db.get(Resume, saved.resume_id)
    if resume is None:
        logger.warning("saved search %s references missing resume %s", saved.id, saved.resume_id)
        return {"error": "resume missing"}

    run, new_jobs, matches = await run_search(
        db,
        resume,
        location=saved.location,
        remote_only=saved.remote_only,
        saved_search_id=saved.id,
    )

    good = [m for m in matches if m.score >= saved.min_score]
    if saved.email and good and new_jobs:
        _send_digest(saved.email, resume, good[:15])
    return {"run_id": run.id, "new_jobs": new_jobs, "matches_above_threshold": len(good)}


def _send_digest(to_email: str, resume: Resume, matches: list[JobMatch]) -> None:
    settings = get_settings()
    if not (settings.smtp_host and settings.smtp_from):
        logger.info("SMTP not configured; skipping email digest")
        return

    lines = [f"Top job matches for {resume.name or 'your resume'}:\n"]
    for m in matches:
        lines.append(f"[{m.score}] {m.job.title} @ {m.job.company} ({m.job.location or 'n/a'})\n  {m.job.url}\n")
    body = "\n".join(lines)

    msg = MIMEText(body)
    msg["Subject"] = f"AI Job Finder: {len(matches)} new matches"
    msg["From"] = settings.smtp_from
    msg["To"] = to_email

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
            server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        logger.info("digest sent to %s", to_email)
    except Exception:  # noqa: BLE001
        logger.exception("failed to send digest email")
