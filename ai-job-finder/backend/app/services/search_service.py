"""Search orchestration: fan out to connectors, dedupe, persist, score.

Failure isolation: each connector runs under its own timeout; an exception from one
source is recorded in run stats and never fails the search.
"""
from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..connectors import JobPosting, SearchQuery, build_connectors
from ..models import Job, JobMatch, Resume, SearchRun
from .match_scorer import detect_fresher_friendly, extract_years_demand, score_match
from .role_scorer import score_roles
from .skill_extractor import extract_skills

logger = logging.getLogger(__name__)


def _dedupe_key(title: str, company: str) -> str:
    norm = lambda s: re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()  # noqa: E731
    return f"{norm(title)}::{norm(company)}"[:500]


def build_search_keywords(resume: Resume, roles_override: list[str] | None) -> tuple[list[str], list[str]]:
    """Return (keywords for connectors, role titles for the title component)."""
    role_fits = score_roles(resume.skills or [], resume.raw_text or "")
    top_roles = role_fits[:3]

    role_titles: list[str] = []
    if roles_override:
        role_titles = [r.lower() for r in roles_override]
    else:
        for fit in top_roles:
            role_titles.extend(fit.titles[:2])

    # Connector keywords: role titles + a few strong resume skills.
    strong_skills = (resume.skills or [])[:5]
    keywords = list(dict.fromkeys(role_titles + strong_skills))  # de-dup, keep order
    return keywords[:12], role_titles


async def _run_connector(connector, query: SearchQuery, client: httpx.AsyncClient, timeout: float):
    return await asyncio.wait_for(connector.search(query, client), timeout=timeout)


async def fetch_postings(query: SearchQuery) -> tuple[list[JobPosting], dict]:
    """Run all enabled connectors concurrently; return (postings, per-source stats)."""
    settings = get_settings()
    connectors = [c for c in build_connectors(settings)]
    stats: dict[str, dict] = {}
    enabled = []
    for c in connectors:
        if c.enabled:
            enabled.append(c)
        else:
            stats[c.id] = {"fetched": 0, "error": f"disabled: missing {', '.join(c.missing_config) or 'config'}"}

    async with httpx.AsyncClient(timeout=settings.connector_timeout_seconds, follow_redirects=True) as client:
        results = await asyncio.gather(
            *(_run_connector(c, query, client, settings.connector_timeout_seconds + 2) for c in enabled),
            return_exceptions=True,
        )

    postings: list[JobPosting] = []
    for connector, result in zip(enabled, results):
        if isinstance(result, BaseException):
            logger.warning("connector %s failed: %s", connector.id, result)
            stats[connector.id] = {"fetched": 0, "error": f"{type(result).__name__}: {result}"}
        else:
            stats[connector.id] = {"fetched": len(result), "error": None}
            postings.extend(result)
    return postings, stats


def persist_and_score(
    db: Session,
    resume: Resume,
    postings: list[JobPosting],
    role_titles: list[str],
    wanted_location: str | None,
    remote_only: bool,
) -> tuple[int, list[JobMatch]]:
    """Dedupe postings into jobs table, score each against the resume. Returns (new_jobs, matches)."""
    new_jobs = 0
    seen_keys: set[str] = set()
    matches: list[JobMatch] = []

    for posting in postings:
        if not posting.title or not posting.url:
            continue
        key = _dedupe_key(posting.title, posting.company)
        if key in seen_keys:
            continue
        seen_keys.add(key)

        job = db.scalar(select(Job).where(Job.dedupe_key == key))
        if job is None:
            job = Job(
                dedupe_key=key,
                title=posting.title[:300],
                company=posting.company[:200],
                location=posting.location[:200],
                remote=posting.remote,
                description=posting.description,
                required_skills=extract_skills(f"{posting.title} {posting.description}"),
                experience_required=(
                    f"{extract_years_demand(posting.title, posting.description)}+ years"
                    if extract_years_demand(posting.title, posting.description) is not None
                    else ("Fresher friendly" if detect_fresher_friendly(posting.title, posting.description) else None)
                ),
                fresher_friendly=detect_fresher_friendly(posting.title, posting.description),
                salary=posting.salary,
                url=posting.url,
                source=posting.source,
                posted_at=posting.posted_at,
            )
            db.add(job)
            db.flush()
            new_jobs += 1

        result = score_match(
            resume_skills=resume.skills or [],
            resume_years=resume.experience_years or 0.0,
            target_roles=resume.target_roles or [],
            role_titles=role_titles,
            job_title=job.title,
            job_description=job.description,
            job_skills=job.required_skills or [],
            job_location=job.location,
            job_remote=job.remote,
            job_source=job.source,
            posted_at=job.posted_at,
            wanted_location=wanted_location,
            remote_only=remote_only,
        )

        match = db.scalar(select(JobMatch).where(JobMatch.resume_id == resume.id, JobMatch.job_id == job.id))
        if match is None:
            match = JobMatch(resume_id=resume.id, job_id=job.id)
            db.add(match)
        match.score = result.score
        match.components = result.components
        match.matched_skills = result.matched_skills
        match.missing_skills = result.missing_skills
        match.shortlist_chance = result.shortlist_chance
        match.application_difficulty = result.application_difficulty
        match.why_apply = result.why_apply
        matches.append(match)

    db.flush()
    matches.sort(key=lambda m: m.score, reverse=True)
    return new_jobs, matches


async def run_search(
    db: Session,
    resume: Resume,
    *,
    location: str | None = None,
    remote_only: bool = False,
    roles_override: list[str] | None = None,
    limit_per_source: int = 30,
    saved_search_id: int | None = None,
) -> tuple[SearchRun, int, list[JobMatch]]:
    """End-to-end search: build query → fetch → persist → score. Returns (run, new_jobs, matches)."""
    keywords, role_titles = build_search_keywords(resume, roles_override)
    query = SearchQuery(keywords=keywords, location=location, remote_only=remote_only, limit=limit_per_source)

    run = SearchRun(resume_id=resume.id, saved_search_id=saved_search_id)
    db.add(run)
    db.flush()

    postings, stats = await fetch_postings(query)
    new_jobs, matches = persist_and_score(db, resume, postings, role_titles, location, remote_only)

    run.finished_at = datetime.now(timezone.utc)
    run.stats = {"sources": stats, "keywords": keywords, "total_fetched": len(postings), "new_jobs": new_jobs}
    db.commit()
    return run, new_jobs, matches
