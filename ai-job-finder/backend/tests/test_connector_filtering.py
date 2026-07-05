from app.connectors.base import matches_keywords
from app.services.skill_extractor import extract_job_skills


def test_short_skill_does_not_substring_match():
    # "c" as a keyword must not match "casino" or "creative".
    assert not matches_keywords("Online Casino Game Tester", ["c"])
    assert not matches_keywords("VP Creative", ["c"])
    assert matches_keywords("Embedded developer: C, C++ and Rust", ["c"])


def test_multiword_keyword_requires_all_words():
    assert matches_keywords("Junior Software Engineer (Backend)", ["junior software engineer"])
    assert not matches_keywords("Junior Accountant", ["junior software engineer"])
    # Words may appear anywhere, not necessarily adjacent.
    assert matches_keywords("Software Engineer, Junior level", ["junior software engineer"])


def test_any_keyword_is_sufficient():
    assert matches_keywords("Data Analyst - SQL dashboards", ["python developer", "data analyst"])


def test_empty_keywords_match_everything():
    assert matches_keywords("anything", [])


def test_job_skills_drop_risky_short_names_in_prose():
    # Hospitality posting where "r" / "c" / "go" would only appear as prose noise.
    assert extract_job_skills("Supervisora de Operações e Reservas. Go to our site c/o HR.") == []


def test_job_skills_keep_short_names_in_technical_context():
    text = "Looking for a developer with C, Python, Linux and Git experience plus SQL."
    skills = extract_job_skills(text)
    assert "c" in skills
    assert "python" in skills
