"""Saved searches (daily automation) and run history."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Resume, SavedSearch, SearchRun
from ..schemas import SavedSearchCreate, SavedSearchOut, SearchRunOut
from ..services.scheduler import run_saved_search

router = APIRouter(prefix="/automation", tags=["automation"])


@router.post("/schedules", response_model=SavedSearchOut, status_code=201)
def create_schedule(payload: SavedSearchCreate, db: Session = Depends(get_db)):
    if db.get(Resume, payload.resume_id) is None:
        raise HTTPException(404, "Resume not found.")
    saved = SavedSearch(**payload.model_dump())
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


@router.get("/schedules", response_model=list[SavedSearchOut])
def list_schedules(db: Session = Depends(get_db)):
    return db.scalars(select(SavedSearch).order_by(SavedSearch.created_at.desc())).all()


@router.delete("/schedules/{schedule_id}", status_code=204)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    saved = db.get(SavedSearch, schedule_id)
    if saved is None:
        raise HTTPException(404, "Schedule not found.")
    db.delete(saved)
    db.commit()


@router.post("/schedules/{schedule_id}/run")
async def trigger_schedule(schedule_id: int, db: Session = Depends(get_db)):
    saved = db.get(SavedSearch, schedule_id)
    if saved is None:
        raise HTTPException(404, "Schedule not found.")
    return await run_saved_search(db, saved)


@router.get("/runs", response_model=list[SearchRunOut])
def list_runs(saved_search_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(SearchRun).order_by(SearchRun.started_at.desc()).limit(50)
    if saved_search_id is not None:
        stmt = stmt.where(SearchRun.saved_search_id == saved_search_id)
    return db.scalars(stmt).all()
