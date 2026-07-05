from app.services.resume_parser import parse_resume, split_sections

SAMPLE = """Priya Sharma
priya.sharma@example.com | +91 98765 43210 | Bengaluru

Objective
Aspiring Data Analyst with strong Python and SQL skills.

Education
B.Tech in Computer Science, IIT Delhi, 2024

Skills
Python, SQL, Pandas, NumPy, Excel, Power BI, Statistics

Projects
Sales Dashboard
Built an interactive Power BI dashboard analyzing 50k sales records.

Churn Prediction
Trained a scikit-learn model reaching 84% accuracy on customer churn.

Experience
Data Analyst Intern
Acme Analytics, Jan 2024 - Jun 2024. Cleaned datasets and automated weekly reports with Python.

Certifications
Google Data Analytics Certificate
"""


def test_sections_split():
    sections = split_sections(SAMPLE)
    assert "education" in sections
    assert "skills" in sections
    assert "projects" in sections
    assert "experience" in sections


def test_contact_parsing():
    parsed = parse_resume(SAMPLE)
    assert parsed.name == "Priya Sharma"
    assert parsed.email == "priya.sharma@example.com"
    assert parsed.phone is not None


def test_skills_and_roles():
    parsed = parse_resume(SAMPLE)
    for expected in ("python", "sql", "pandas", "excel", "power bi", "statistics"):
        assert expected in parsed.skills, expected
    assert "Data Analyst" in parsed.target_roles


def test_education_and_certs():
    parsed = parse_resume(SAMPLE)
    assert parsed.education, "expected at least one education entry"
    assert parsed.education[0]["year"] == "2024"
    assert any("Google" in c for c in parsed.certifications)


def test_experience_years_from_date_range():
    parsed = parse_resume(SAMPLE)
    # Jan 2024 – Jun 2024 ≈ 0.4 years
    assert 0.2 <= parsed.experience_years <= 0.8
