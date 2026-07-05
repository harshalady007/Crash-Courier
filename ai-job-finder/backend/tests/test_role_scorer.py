from app.services.role_scorer import score_roles


def test_data_analyst_profile_ranks_first():
    skills = ["python", "sql", "excel", "data analysis", "data visualization", "statistics", "power bi", "pandas"]
    text = "built dashboards and reports with kpi insights for business intelligence"
    results = score_roles(skills, text)
    assert results[0].role_name == "Data Analyst"
    assert results[0].score >= 80
    assert "sql" in results[0].matched_skills


def test_explanations_mention_missing_skills():
    results = score_roles(["python"], "")
    analyst = next(r for r in results if r.role_name == "Data Analyst")
    assert "missing" in analyst.explanation
    assert "sql" in analyst.missing_skills


def test_scores_bounded():
    for result in score_roles([], ""):
        assert 0 <= result.score <= 100
