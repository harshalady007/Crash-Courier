"""Search execution, job/match listing with filters, sources, recommendations."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..config import get_settings
from ..connectors import build_connectors
from ..database import get_db
from ..models import Job, JobMatch, Resume
from ..schemas import (
    JobMatchOut,
    RecommendationOut,
    SearchRequest,
    SearchResultOut,
    SourceOut,
)
from ..services.recommender import build_recommendation
from ..services.search_service import run_search

router = APIRouter(tags=["jobs"])

POSTED_WITHIN = {"24h": timedelta(hours=24), "7d": timedelta(days=7), "30d": timedelta(days=30)}


@router.post("/search", response_model=SearchResultOut)
async def search_jobs(payload: SearchRequest, db: Session = Depends(get_db)):
    resume = db.get(Resume, payload.resume_id)
    if resume is None:
        raise HTTPException(404, "Resume not found. Upload a resume first.")

    run, new_jobs, matches = await run_search(
        db,
        resume,
        location=payload.location,
        remote_only=payload.remote_only,
        roles_override=payload.roles,
        limit_per_source=payload.limit_per_source,
    )
    return SearchResultOut(
        run_id=run.id,
        stats=run.stats,
        total_jobs=len(matches),
        new_jobs=new_jobs,
        matches=[JobMatchOut.model_validate(m) for m in matches[:100]],
    )


@router.get("/jobs", response_model=list[JobMatchOut])
def list_jobs(
    resume_id: int,
    min_score: int = Query(default=0, ge=0, le=100),
    remote_only: bool = False,
    fresher_only: bool = False,
    internship: bool = False,
    full_time: bool = False,
    location: str | None = None,
    role: str | None = None,
    posted_within: str | None = Query(default=None, pattern="^(24h|7d|30d)$"),
    sort: str = Query(default="score", pattern="^(score|date)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    stmt = (
        select(JobMatch)
        .join(Job)
        .options(joinedload(JobMatch.job))
        .where(JobMatch.resume_id == resume_id, JobMatch.score >= min_score)
    )
    if remote_only:
        stmt = stmt.where(Job.remote.is_(True))
    if fresher_only:
        stmt = stmt.where(Job.fresher_friendly.is_(True))
    if internship:
        stmt = stmt.where(Job.title.ilike("%intern%"))
    if full_time:
        stmt = stmt.where(~Job.title.ilike("%intern%"))
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location}%"))
    if role:
        stmt = stmt.where(Job.title.ilike(f"%{role}%"))
    if posted_within:
        cutoff = datetime.now(timezone.utc) - POSTED_WITHIN[posted_within]
        stmt = stmt.where(Job.posted_at >= cutoff)

    if sort == "date":
        stmt = stmt.order_by(Job.posted_at.desc().nullslast())
    else:
        stmt = stmt.order_by(JobMatch.score.desc())

    return db.scalars(stmt.limit(limit).offset(offset)).all()


@router.get("/jobs/{match_id}", response_model=JobMatchOut)
def get_job_match(match_id: int, db: Session = Depends(get_db)):
    match = db.get(JobMatch, match_id)
    if match is None:
        raise HTTPException(404, "Match not found.")
    return match


@router.post("/jobs/{match_id}/recommend", response_model=RecommendationOut)
def recommend(match_id: int, db: Session = Depends(get_db)):
    match = db.get(JobMatch, match_id)
    if match is None:
        raise HTTPException(404, "Match not found.")
    resume = db.get(Resume, match.resume_id)
    job = db.get(Job, match.job_id)

    if match.recommendation:  # cached — regenerate by deleting first (future: ?force=1)
        return match.recommendation

    recommendation = build_recommendation(resume, job, match)
    match.recommendation = recommendation
    db.commit()
    return recommendation


@router.get("/sources", response_model=list[SourceOut])
def list_sources():
    settings = get_settings()
    return [
        SourceOut(id=c.id, name=c.name, enabled=c.enabled, missing_config=c.missing_config)
        for c in build_connectors(settings)
    ]
