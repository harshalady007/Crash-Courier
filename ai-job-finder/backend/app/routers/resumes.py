"""Resume upload, parsing, editing, and role analysis endpoints."""
from __future__ import annotations

import anyio
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Resume, RoleFit
from ..schemas import ResumeOut, ResumeUpdate, RoleFitOut
from ..services.resume_parser import UnsupportedFileError, extract_text, parse_resume
from ..services.role_scorer import score_roles

router = APIRouter(prefix="/resumes", tags=["resumes"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("", response_model=ResumeOut, status_code=201)
async def upload_resume(file: UploadFile, db: Session = Depends(get_db)):
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Resume file exceeds the 10 MB limit.")
    if not content:
        raise HTTPException(400, "Empty file.")

    filename = file.filename or "resume.pdf"
    try:
        # PyMuPDF parsing is CPU-bound — keep it off the event loop.
        text = await anyio.to_thread.run_sync(extract_text, filename, content)
    except UnsupportedFileError as exc:
        raise HTTPException(415, str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 — corrupt files come in all shapes
        raise HTTPException(422, f"Could not read the file: {exc}") from exc

    if not text.strip():
        raise HTTPException(422, "No text could be extracted — is this a scanned image PDF?")

    parsed = parse_resume(text)
    resume = Resume(
        filename=filename,
        raw_text=text,
        name=parsed.name,
        email=parsed.email,
        phone=parsed.phone,
        skills=parsed.skills,
        tools=parsed.tools,
        education=parsed.education,
        projects=parsed.projects,
        experience=parsed.experience,
        certifications=parsed.certifications,
        target_roles=parsed.target_roles,
        experience_years=parsed.experience_years,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_db)):
    return db.scalars(select(Resume).order_by(Resume.created_at.desc())).all()


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if resume is None:
        raise HTTPException(404, "Resume not found.")
    return resume


@router.patch("/{resume_id}", response_model=ResumeOut)
def update_resume(resume_id: int, payload: ResumeUpdate, db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if resume is None:
        raise HTTPException(404, "Resume not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(resume, field, value)
    db.commit()
    db.refresh(resume)
    return resume


@router.delete("/{resume_id}", status_code=204)
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if resume is None:
        raise HTTPException(404, "Resume not found.")
    db.delete(resume)
    db.commit()


@router.post("/{resume_id}/analyze", response_model=list[RoleFitOut])
def analyze_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if resume is None:
        raise HTTPException(404, "Resume not found.")

    # Replace previous analysis for this resume.
    for old in db.scalars(select(RoleFit).where(RoleFit.resume_id == resume_id)).all():
        db.delete(old)

    fits = []
    for result in score_roles(resume.skills or [], resume.raw_text or ""):
        fit = RoleFit(
            resume_id=resume_id,
            role_name=result.role_name,
            score=result.score,
            matched_skills=result.matched_skills,
            missing_skills=result.missing_skills,
            explanation=result.explanation,
        )
        db.add(fit)
        fits.append(fit)
    db.commit()
    for fit in fits:
        db.refresh(fit)
    return fits
