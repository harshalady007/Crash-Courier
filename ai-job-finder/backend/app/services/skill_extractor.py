"""Taxonomy-based skill extraction.

Matches canonical skills and their aliases in free text using word-boundary regexes.
Used on both resume text and job descriptions so both sides speak the same skill ids.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache

from ..config import data_path


@lru_cache
def _load_taxonomy() -> list[dict]:
    with open(data_path("skills_taxonomy.json"), encoding="utf-8") as f:
        return json.load(f)["skills"]


@lru_cache
def _compiled_patterns() -> list[tuple[str, re.Pattern]]:
    """One compiled alternation pattern per canonical skill."""
    patterns: list[tuple[str, re.Pattern]] = []
    for entry in _load_taxonomy():
        terms = [entry["id"], *entry.get("aliases", [])]
        # \b doesn't work adjacent to symbols like "c++" or "c#", so use lookarounds
        # that treat word chars, '+', and '#' as part of a token.
        alternation = "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True))
        pattern = re.compile(rf"(?<![\w+#])(?:{alternation})(?![\w+#])", re.IGNORECASE)
        patterns.append((entry["id"], pattern))
    return patterns


def extract_skills(text: str) -> list[str]:
    """Return canonical skill ids found in text, in taxonomy order."""
    if not text:
        return []
    found: list[str] = []
    for skill_id, pattern in _compiled_patterns():
        if pattern.search(text):
            found.append(skill_id)
    return found


# One/two-letter language names false-positive constantly in prose ("c." in lists,
# "R" initials, "go to"). Trust them on resumes (explicit skills sections) but not
# on job descriptions unless the posting is clearly technical.
RISKY_SHORT_SKILLS = {"c", "r", "go"}


def extract_job_skills(text: str) -> list[str]:
    """Skill extraction tuned for job postings: drop risky short skills unless
    at least three other skills confirm a technical context."""
    skills = extract_skills(text)
    solid = [s for s in skills if s not in RISKY_SHORT_SKILLS]
    return skills if len(solid) >= 3 else solid


def skill_categories() -> dict[str, str]:
    return {entry["id"]: entry["category"] for entry in _load_taxonomy()}


def tools_subset(skills: list[str]) -> list[str]:
    """Skills that are concrete tools/technologies rather than concepts."""
    concept_categories = {"soft", "process", "cs", "business"}
    cats = skill_categories()
    return [s for s in skills if cats.get(s) not in concept_categories]
