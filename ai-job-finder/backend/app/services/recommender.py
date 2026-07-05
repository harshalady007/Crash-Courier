"""Per-job AI recommendations: why-fit, keywords to add, cover letter, recruiter message.

Uses Claude when configured; otherwise deterministic templates so the feature always works.
Scores are never produced here — see docs/06.
"""
from __future__ import annotations

import json
import logging

from ..models import Job, JobMatch, Resume
from .llm import generate_text, llm_available

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are a career coach for early-career candidates. Write concise, specific, "
    "honest application materials. Never invent experience the candidate does not have."
)


def _priority(match: JobMatch) -> str:
    if match.score >= 75 and match.shortlist_chance == "High":
        return "High"
    if match.score >= 55:
        return "Medium"
    return "Low"


def build_recommendation(resume: Resume, job: Job, match: JobMatch) -> dict:
    """Returns the recommendation dict (also cached on the match by the router)."""
    priority = _priority(match)

    if llm_available():
        result = _llm_recommendation(resume, job, match, priority)
        if result is not None:
            return result

    return _template_recommendation(resume, job, match, priority)


# ---------------------------------------------------------------- LLM path

def _llm_recommendation(resume: Resume, job: Job, match: JobMatch, priority: str) -> dict | None:
    prompt = f"""Candidate profile:
- Name: {resume.name or "The candidate"}
- Skills: {", ".join(resume.skills or [])[:400]}
- Experience: {resume.experience_years} years. {json.dumps((resume.experience or [])[:3])[:600]}
- Education: {json.dumps((resume.education or [])[:2])[:300]}
- Projects: {json.dumps((resume.projects or [])[:3])[:600]}

Job posting:
- Title: {job.title}
- Company: {job.company}
- Location: {job.location or "n/a"} (remote: {job.remote})
- Description (excerpt): {(job.description or "")[:1500]}

Match analysis (computed): score {match.score}/100, matched skills: {", ".join(match.matched_skills)},
missing skills: {", ".join(match.missing_skills) or "none"}.

Return ONLY a JSON object with exactly these keys:
- "why_fit": 2-3 sentences on why this candidate fits this job.
- "keywords_to_add": array of up to 6 resume keywords/phrases to add for this job.
- "cover_letter": a tailored cover letter, ~220 words, plain text, no placeholders left unfilled
  except [Hiring Manager] where the name is unknown.
- "linkedin_message": a recruiter outreach message under 300 characters.
"""
    text = generate_text(prompt, system=_SYSTEM, max_tokens=1500)
    if not text:
        return None
    try:
        # Tolerate code fences around the JSON.
        cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(cleaned)
        return {
            "why_fit": str(data["why_fit"]),
            "keywords_to_add": [str(k) for k in data.get("keywords_to_add", [])][:6],
            "cover_letter": str(data["cover_letter"]),
            "linkedin_message": str(data["linkedin_message"])[:300],
            "priority": priority,
            "generated_by": "llm",
        }
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("LLM recommendation parse failed: %s", exc)
        return None


# ---------------------------------------------------------------- template fallback

def _template_recommendation(resume: Resume, job: Job, match: JobMatch, priority: str) -> dict:
    name = resume.name or "I"
    matched = ", ".join(match.matched_skills[:5]) or "relevant technical skills"
    top_project = (resume.projects or [{}])[0].get("title", "") if resume.projects else ""

    why_fit = (
        f"Your profile matches {len(match.matched_skills)} of the skills this role asks for ({matched}). "
        + ("The posting is fresher-friendly, which fits your experience level. " if job.fresher_friendly else "")
        + (f"Focus on closing the gap in: {', '.join(match.missing_skills[:3])}." if match.missing_skills else "")
    ).strip()

    cover_letter = f"""Dear [Hiring Manager],

I am writing to apply for the {job.title} position at {job.company}. As an early-career candidate with hands-on experience in {matched}, I am confident I can contribute from day one.

{f"In my project '{top_project}', I applied these skills to deliver a working solution end to end. " if top_project else ""}My background ({resume.experience_years} years of practical experience, including projects and internships) has given me a strong foundation in solving real problems with data and code, and I learn new tools quickly.

What draws me to this role is the opportunity to grow within a team that values {", ".join(match.matched_skills[:2]) or "strong engineering"}. I would welcome the chance to discuss how my skills align with your needs.

Thank you for your time and consideration.

Sincerely,
{resume.name or "[Your Name]"}"""

    linkedin_message = (
        f"Hi, I just applied for the {job.title} role at {job.company}. "
        f"My background in {', '.join(match.matched_skills[:2]) or 'this area'} is a close match — "
        f"I'd love to be considered. Happy to share more. Thank you!"
    )[:300]

    return {
        "why_fit": why_fit,
        "keywords_to_add": match.missing_skills[:6],
        "cover_letter": cover_letter,
        "linkedin_message": linkedin_message,
        "priority": priority,
        "generated_by": "template",
    }
