"""Pydantic request/response schemas — the API contract (see docs/04-api-routes.md)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Resumes ----------

class EducationItem(BaseModel):
    degree: str = ""
    institution: str = ""
    year: str = ""


class ResumeOut(ORMModel):
    id: int
    filename: str
    name: str | None
    email: str | None
    phone: str | None
    skills: list[str]
    tools: list[str]
    education: list[dict]
    projects: list[dict]
    experience: list[dict]
    certifications: list[str]
    target_roles: list[str]
    experience_years: float
    created_at: datetime


class ResumeUpdate(BaseModel):
    name: str | None = None
    skills: list[str] | None = None
    target_roles: list[str] | None = None
    experience_years: float | None = None


class RoleFitOut(ORMModel):
    id: int
    role_name: str
    score: int
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str


# ---------- Search & Jobs ----------

class SearchRequest(BaseModel):
    resume_id: int
    location: str | None = None
    remote_only: bool = False
    roles: list[str] | None = None  # override auto-selected roles
    limit_per_source: int = Field(default=30, ge=1, le=100)


class JobOut(ORMModel):
    id: int
    title: str
    company: str
    location: str
    remote: bool
    description: str
    required_skills: list[str]
    experience_required: str | None
    fresher_friendly: bool
    salary: str | None
    url: str
    source: str
    posted_at: datetime | None


class JobMatchOut(ORMModel):
    id: int
    score: int
    components: dict
    matched_skills: list[str]
    missing_skills: list[str]
    shortlist_chance: str
    application_difficulty: str
    why_apply: str
    recommendation: dict | None
    job: JobOut


class SearchResultOut(BaseModel):
    run_id: int
    stats: dict
    total_jobs: int
    new_jobs: int
    matches: list[JobMatchOut]


class SourceOut(BaseModel):
    id: str
    name: str
    enabled: bool
    missing_config: list[str]


# ---------- Recommendations ----------

class RecommendationOut(BaseModel):
    why_fit: str
    keywords_to_add: list[str]
    cover_letter: str
    linkedin_message: str
    priority: str
    generated_by: str  # "llm" | "template"


# ---------- Automation ----------

class SavedSearchCreate(BaseModel):
    resume_id: int
    location: str | None = None
    remote_only: bool = False
    min_score: int = Field(default=60, ge=0, le=100)
    email: str | None = None


class SavedSearchOut(ORMModel):
    id: int
    resume_id: int
    location: str | None
    remote_only: bool
    min_score: int
    email: str | None
    schedule: str
    active: bool
    created_at: datetime


class SearchRunOut(ORMModel):
    id: int
    saved_search_id: int | None
    resume_id: int
    started_at: datetime
    finished_at: datetime | None
    stats: dict
