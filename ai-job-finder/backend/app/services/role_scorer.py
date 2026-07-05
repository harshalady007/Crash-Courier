"""Role-fit scoring: resume skills/text → 0–100 fit per role profile.

score = 100 * (0.60 * core_coverage + 0.25 * bonus_coverage + 0.15 * keyword_coverage)
See docs/06-matching-algorithm.md.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache

from ..config import data_path

CORE_WEIGHT = 0.60
BONUS_WEIGHT = 0.25
KEYWORD_WEIGHT = 0.15


@lru_cache
def load_role_profiles() -> list[dict]:
    with open(data_path("role_profiles.json"), encoding="utf-8") as f:
        return json.load(f)["roles"]


@dataclass
class RoleFitResult:
    role_name: str
    score: int
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str
    titles: list[str]  # search query titles for this role


def _coverage(have: set[str], want: list[str]) -> tuple[list[str], list[str], float]:
    matched = [s for s in want if s in have]
    missing = [s for s in want if s not in have]
    ratio = len(matched) / len(want) if want else 0.0
    return matched, missing, ratio


def score_roles(resume_skills: list[str], resume_text: str) -> list[RoleFitResult]:
    """Score every role profile against the resume; sorted best-first."""
    have = set(resume_skills)
    text_lower = (resume_text or "").lower()
    results: list[RoleFitResult] = []

    for role in load_role_profiles():
        core_matched, core_missing, core_ratio = _coverage(have, role["core_skills"])
        bonus_matched, _, bonus_ratio = _coverage(have, role["bonus_skills"])

        keywords = role.get("keywords", [])
        keyword_hits = [
            k for k in keywords
            if re.search(rf"(?<!\w){re.escape(k)}(?!\w)", text_lower)
        ]
        keyword_ratio = len(keyword_hits) / len(keywords) if keywords else 0.0

        score = round(100 * (CORE_WEIGHT * core_ratio + BONUS_WEIGHT * bonus_ratio + KEYWORD_WEIGHT * keyword_ratio))

        explanation_parts = [
            f"Matches {len(core_matched)}/{len(role['core_skills'])} core skills"
            + (f" ({', '.join(core_matched)})" if core_matched else "")
        ]
        if core_missing:
            explanation_parts.append(f"missing: {', '.join(core_missing)}")
        if bonus_matched:
            explanation_parts.append(f"bonus skills: {', '.join(bonus_matched)}")
        if keyword_hits:
            explanation_parts.append(f"relevant experience keywords: {', '.join(keyword_hits)}")

        results.append(RoleFitResult(
            role_name=role["name"],
            score=score,
            matched_skills=core_matched + bonus_matched,
            missing_skills=core_missing,
            explanation="; ".join(explanation_parts) + ".",
            titles=role["titles"],
        ))

    results.sort(key=lambda r: r.score, reverse=True)
    return results
