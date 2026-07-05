"""Job-match scoring: (resume, job posting) → weighted 0–100 score with components.

Deterministic and explainable by design — the LLM never produces these numbers.
See docs/06-matching-algorithm.md for the rationale behind each weight.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone

WEIGHTS = {
    "skills": 0.40,
    "title": 0.20,
    "experience": 0.15,
    "location": 0.10,
    "recency": 0.10,
    "source": 0.05,
}

FRESHER_RE = re.compile(
    r"fresher|entry[- ]level|0[- ]?[12]\s*year|no experience|recent graduate|intern(?:ship)?"
    r"|graduate (?:trainee|engineer|program)|junior|early career",
    re.IGNORECASE,
)
YEARS_DEMAND_RE = re.compile(r"(\d+)\s*\+?\s*(?:-\s*\d+\s*)?(?:years?|yrs?)", re.IGNORECASE)
SENIORITY_RE = re.compile(
    r"\b(senior|staff|principal|lead|sr\.?|director|head of|manager|architect)\b", re.IGNORECASE
)

DIRECT_BOARD_SOURCES = {"greenhouse", "lever"}


@dataclass
class MatchResult:
    score: int
    components: dict
    matched_skills: list[str]
    missing_skills: list[str]
    shortlist_chance: str
    application_difficulty: str
    why_apply: str


def detect_fresher_friendly(title: str, description: str) -> bool:
    return bool(FRESHER_RE.search(f"{title} {description[:2000]}"))


def extract_years_demand(title: str, description: str) -> int | None:
    """Smallest explicit years-of-experience demand found in the posting, if any."""
    demands = [int(m.group(1)) for m in YEARS_DEMAND_RE.finditer(f"{title} {description[:2000]}")]
    demands = [d for d in demands if d <= 15]  # ignore "20 years of company history" noise
    return min(demands) if demands else None


def _skills_component(resume_skills: set[str], job_skills: list[str], description: str) -> tuple[int, list[str], list[str]]:
    if job_skills:
        matched = [s for s in job_skills if s in resume_skills]
        missing = [s for s in job_skills if s not in resume_skills]
        return round(100 * len(matched) / len(job_skills)), matched, missing
    # No recognizable required skills — weak fallback on description overlap, capped.
    desc_lower = description.lower()
    overlap = [s for s in resume_skills if s in desc_lower]
    return (60 if overlap else 30), overlap[:10], []


def _title_component(job_title: str, role_titles: list[str], target_roles: list[str]) -> int:
    title_lower = job_title.lower()
    candidates = [t.lower() for t in role_titles + target_roles]
    if any(c in title_lower or title_lower in c for c in candidates if c):
        return 100
    # Partial: share a significant word (analyst, engineer, developer, scientist, intern…)
    title_words = set(re.findall(r"[a-z]+", title_lower))
    for c in candidates:
        if set(re.findall(r"[a-z]+", c)) & title_words & {
            "analyst", "engineer", "developer", "scientist", "intern", "python",
            "data", "machine", "software", "automation", "business", "ai", "ml",
        }:
            return 60
    return 20


def _experience_component(
    fresher_friendly: bool, years_demand: int | None, resume_years: float, senior_title: bool
) -> int:
    # A senior/staff/lead title is a hard signal regardless of what the description says.
    if senior_title and resume_years < 4:
        return 10
    if fresher_friendly and resume_years <= 2:
        return 100
    if years_demand is None:
        return 50 if not fresher_friendly else 85
    if resume_years >= years_demand:
        return 95
    gap = years_demand - resume_years
    if gap <= 1:
        return 70
    if gap <= 2:
        return 40
    return 10


def _location_component(job_location: str, job_remote: bool, wanted_location: str | None, remote_only: bool) -> int:
    if job_remote:
        return 100
    if remote_only:
        return 20  # user wants remote, job isn't
    if not wanted_location:
        return 50
    wanted = wanted_location.lower().strip()
    job_loc = (job_location or "").lower()
    if not job_loc:
        return 50
    if wanted in job_loc or job_loc in wanted:
        return 100
    # Same last token (often country) is a weak positive.
    if wanted.split(",")[-1].strip() and wanted.split(",")[-1].strip() in job_loc:
        return 70
    return 30


def _recency_component(posted_at: datetime | None) -> int:
    if posted_at is None:
        return 50
    now = datetime.now(timezone.utc)
    if posted_at.tzinfo is None:
        posted_at = posted_at.replace(tzinfo=timezone.utc)
    age_hours = (now - posted_at).total_seconds() / 3600
    if age_hours <= 24:
        return 100
    if age_hours <= 24 * 7:
        return 85
    if age_hours <= 24 * 30:
        return 60
    return 30


def _source_component(source: str) -> int:
    return 100 if source in DIRECT_BOARD_SOURCES else 70


def _band(score: int) -> str:
    if score >= 75:
        return "High"
    if score >= 55:
        return "Medium"
    return "Low"


def _downgrade(band: str) -> str:
    return {"High": "Medium", "Medium": "Low", "Low": "Low"}[band]


def score_match(
    *,
    resume_skills: list[str],
    resume_years: float,
    target_roles: list[str],
    role_titles: list[str],
    job_title: str,
    job_description: str,
    job_skills: list[str],
    job_location: str,
    job_remote: bool,
    job_source: str,
    posted_at: datetime | None,
    wanted_location: str | None,
    remote_only: bool,
) -> MatchResult:
    resume_skill_set = set(resume_skills)
    senior_title = bool(SENIORITY_RE.search(job_title))
    fresher = detect_fresher_friendly(job_title, job_description) and not senior_title
    years_demand = extract_years_demand(job_title, job_description)

    skills_score, matched, missing = _skills_component(resume_skill_set, job_skills, job_description)
    raw = {
        "skills": skills_score,
        "title": _title_component(job_title, role_titles, target_roles),
        "experience": _experience_component(fresher, years_demand, resume_years, senior_title),
        "location": _location_component(job_location, job_remote, wanted_location, remote_only),
        "recency": _recency_component(posted_at),
        "source": _source_component(job_source),
    }

    score = round(sum(raw[k] * w for k, w in WEIGHTS.items()))
    components = {k: {"score": raw[k], "weight": WEIGHTS[k]} for k in WEIGHTS}

    chance = _band(score)
    if raw["experience"] < 40:  # hard experience mismatch dominates real outcomes
        chance = _downgrade(chance)

    if fresher and len(missing) <= 3:
        difficulty = "Low"
    elif len(missing) > 5 or (years_demand is not None and years_demand >= 3):
        difficulty = "High"
    else:
        difficulty = "Medium"

    why = _why_apply(raw, matched, missing, fresher)

    return MatchResult(
        score=score,
        components=components,
        matched_skills=matched,
        missing_skills=missing,
        shortlist_chance=chance,
        application_difficulty=difficulty,
        why_apply=why,
    )


def _why_apply(raw: dict, matched: list[str], missing: list[str], fresher: bool) -> str:
    reasons: list[str] = []
    if raw["skills"] >= 70 and matched:
        reasons.append(f"strong skills overlap ({', '.join(matched[:4])})")
    elif matched:
        reasons.append(f"partial skills overlap ({', '.join(matched[:3])})")
    if fresher:
        reasons.append("fresher-friendly posting")
    if raw["title"] >= 100:
        reasons.append("title matches your target role")
    if raw["recency"] >= 85:
        reasons.append("recently posted")
    if not reasons:
        reasons.append("broad match on your profile")
    sentence = " and ".join(reasons[:2]).capitalize()
    if missing:
        sentence += f". Consider adding: {', '.join(missing[:3])}"
    return sentence + "."
