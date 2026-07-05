from datetime import datetime, timedelta, timezone

from app.services.match_scorer import (
    detect_fresher_friendly,
    extract_years_demand,
    score_match,
)


def _score(**overrides):
    defaults = dict(
        resume_skills=["python", "sql", "pandas"],
        resume_years=0.5,
        target_roles=["Data Analyst"],
        role_titles=["data analyst", "junior data analyst"],
        job_title="Junior Data Analyst",
        job_description="Looking for a fresher with Python and SQL. Entry level role.",
        job_skills=["python", "sql", "excel"],
        job_location="Bengaluru, India",
        job_remote=False,
        job_source="jsearch",
        posted_at=datetime.now(timezone.utc) - timedelta(hours=5),
        wanted_location="Bengaluru",
        remote_only=False,
    )
    defaults.update(overrides)
    return score_match(**defaults)


def test_strong_match_scores_high():
    result = _score()
    assert result.score >= 75
    assert result.shortlist_chance == "High"
    assert result.matched_skills == ["python", "sql"]
    assert result.missing_skills == ["excel"]


def test_experience_mismatch_downgrades_chance():
    result = _score(
        job_title="Senior Data Analyst",
        job_description="Requires 6+ years of experience in analytics.",
    )
    assert result.components["experience"]["score"] <= 40
    assert result.shortlist_chance in ("Medium", "Low")


def test_senior_title_is_hard_penalty_for_freshers():
    result = _score(job_title="Staff Machine Learning Engineer", job_description="Great ML role.")
    assert result.components["experience"]["score"] == 10
    assert result.shortlist_chance in ("Medium", "Low")


def test_fresher_detection():
    assert detect_fresher_friendly("Data Analyst", "This is an entry-level role for freshers")
    assert detect_fresher_friendly("Machine Learning Intern", "")
    assert not detect_fresher_friendly("Staff Engineer", "We need a seasoned architect")


def test_years_demand_extraction():
    assert extract_years_demand("", "Minimum 3 years experience required") == 3
    assert extract_years_demand("", "5+ yrs in Java") == 5
    assert extract_years_demand("", "no explicit demand") is None


def test_score_bounds_and_components():
    result = _score()
    assert 0 <= result.score <= 100
    assert set(result.components) == {"skills", "title", "experience", "location", "recency", "source"}
    assert abs(sum(c["weight"] for c in result.components.values()) - 1.0) < 1e-9
