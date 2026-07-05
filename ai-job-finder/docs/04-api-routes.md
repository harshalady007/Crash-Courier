# API Routes

Base URL: `/api`. All responses JSON. Errors follow FastAPI's `{"detail": ...}` shape.

## Resumes

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/resumes` | multipart `file` (PDF/DOCX) | parsed `ResumeOut` |
| GET | `/resumes` | — | list of resumes (latest first) |
| GET | `/resumes/{id}` | — | `ResumeOut` |
| PATCH | `/resumes/{id}` | partial fields (skills, target_roles, …) | updated `ResumeOut` (user corrections) |
| DELETE | `/resumes/{id}` | — | 204 |
| POST | `/resumes/{id}/analyze` | — | `[RoleFitOut]` sorted by score |

## Search & Jobs

| Method | Path | Body / Query | Returns |
|---|---|---|---|
| POST | `/search` | `{resume_id, location?, remote_only?, roles?, limit_per_source?}` | `SearchResultOut` (run stats + matches) |
| GET | `/jobs` | query: `resume_id` (required), `min_score`, `remote_only`, `fresher_only`, `internship`, `full_time`, `location`, `role`, `posted_within` (`24h`/`7d`/`30d`), `sort` (`score`/`date`), `limit`, `offset` | `[JobMatchOut]` |
| GET | `/jobs/{match_id}` | — | `JobMatchOut` with full job detail |
| GET | `/sources` | — | connector list: id, name, enabled, missing config keys |

## Recommendations

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/jobs/{match_id}/recommend` | — | `RecommendationOut` {why_fit, keywords_to_add, cover_letter, linkedin_message, priority, generated_by: "llm"\|"template"} |

## Automation

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/automation/schedules` | `{resume_id, location?, remote_only?, min_score?, email?}` | `SavedSearchOut` |
| GET | `/automation/schedules` | — | list |
| DELETE | `/automation/schedules/{id}` | — | 204 |
| POST | `/automation/schedules/{id}/run` | — | trigger immediately, returns run stats |
| GET | `/automation/runs` | `?saved_search_id=` | run history |

## Health

| Method | Path | Returns |
|---|---|---|
| GET | `/health` | `{status, version, db, connectors_enabled}` |

### Example: POST /api/search response (abridged)

```json
{
  "run_id": 12,
  "stats": {"remoteok": {"fetched": 40, "error": null}, "adzuna": {"fetched": 0, "error": "disabled: missing ADZUNA_APP_ID"}},
  "total_jobs": 63,
  "new_jobs": 18,
  "matches": [
    {
      "match_id": 481, "score": 84, "shortlist_chance": "High",
      "job": {"title": "Junior Data Analyst", "company": "Acme", "url": "https://…", "source": "jsearch", "remote": true},
      "components": {"skills": {"score": 90, "weight": 0.4}, "title": {"score": 100, "weight": 0.2}},
      "matched_skills": ["python", "sql", "pandas"],
      "missing_skills": ["tableau"],
      "why_apply": "Strong skills overlap (3/4 required) and the posting is fresher-friendly."
    }
  ]
}
```
