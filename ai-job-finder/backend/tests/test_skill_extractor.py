from app.services.skill_extractor import extract_skills


def test_extracts_canonical_skills():
    text = "Proficient in Python, SQL and Power BI. Built dashboards with Tableau."
    skills = extract_skills(text)
    assert "python" in skills
    assert "sql" in skills
    assert "power bi" in skills
    assert "tableau" in skills


def test_aliases_map_to_canonical_id():
    skills = extract_skills("Experience with sklearn, PyTorch and PostgreSQL.")
    assert "scikit-learn" in skills
    assert "pytorch" in skills
    assert "sql" in skills


def test_symbol_skills_do_not_false_positive():
    # "c" must not match inside ordinary words; "c++" must match exactly.
    skills = extract_skills("Studied communication and calculus. Wrote C++ programs.")
    assert "c++" in skills
    assert "c" not in skills


def test_empty_text():
    assert extract_skills("") == []
