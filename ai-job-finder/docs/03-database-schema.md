# Database Schema

SQLite in MVP, PostgreSQL in production — the SQLAlchemy models are dialect-neutral.
JSON columns hold list/dict payloads (native JSONB on Postgres).

```
resumes ──1:N── role_fits
   │
   └──1:N── job_matches ──N:1── jobs
   │
   └──1:N── saved_searches ──1:N── search_runs
```

## Tables

### resumes
| column | type | notes |
|---|---|---|
| id | int PK | |
| filename | text | original upload name |
| raw_text | text | full extracted text |
| name / email / phone | text | parsed contact block |
| skills | json | `["python", "sql", …]` canonical skill ids |
| tools | json | tools/technologies subset |
| education | json | `[{degree, institution, year}]` |
| projects | json | `[{title, description}]` |
| experience | json | `[{title, company, duration}]` |
| certifications | json | `[str]` |
| target_roles | json | roles stated in the resume, if any |
| experience_years | float | estimated total experience |
| created_at | datetime | |

### role_fits
| column | type | notes |
|---|---|---|
| id | int PK | |
| resume_id | FK resumes | |
| role_name | text | e.g. "Data Analyst" |
| score | int 0–100 | |
| matched_skills / missing_skills | json | canonical skill ids |
| explanation | text | human-readable reason |

### jobs  (deduplicated postings)
| column | type | notes |
|---|---|---|
| id | int PK | |
| dedupe_key | text UNIQUE | `norm(title)::norm(company)` |
| title / company | text | |
| location | text | free text from source |
| remote | bool | |
| description | text | may be truncated by source |
| required_skills | json | extracted from description |
| experience_required | text | e.g. "0-1 years", "Fresher" |
| fresher_friendly | bool | detected signal |
| salary | text nullable | as given by source |
| url | text | direct apply link |
| source | text | connector id |
| posted_at | datetime nullable | |
| fetched_at | datetime | |

### job_matches  (job × resume scoring)
| column | type | notes |
|---|---|---|
| id | int PK | |
| resume_id | FK resumes | |
| job_id | FK jobs | UNIQUE(resume_id, job_id) |
| score | int 0–100 | overall |
| components | json | `{skills, title, experience, location, recency}` each 0–100 + weight |
| matched_skills / missing_skills | json | |
| shortlist_chance | text | High / Medium / Low |
| application_difficulty | text | Low / Medium / High |
| why_apply | text | one-line deterministic summary |
| recommendation | json nullable | LLM assets: cover_letter, linkedin_message, keywords_to_add, priority |

### saved_searches  (automation)
| column | type | notes |
|---|---|---|
| id | int PK | |
| resume_id | FK resumes | |
| location / remote_only / min_score | prefs | |
| email | text nullable | digest recipient |
| schedule | text | `daily` (cron in prod) |
| active | bool | |
| created_at | datetime | |

### search_runs
| column | type | notes |
|---|---|---|
| id | int PK | |
| saved_search_id | FK nullable | null = manual run |
| resume_id | FK resumes | |
| started_at / finished_at | datetime | |
| stats | json | per-connector counts, errors, new jobs |

## Indexes
- `jobs.dedupe_key` unique; `jobs.posted_at`, `jobs.source`.
- `job_matches (resume_id, score DESC)` — dashboard sort.
- Production: full-text index on `jobs.description` (Postgres `tsvector`).

## Migration strategy
MVP: `Base.metadata.create_all` on startup. Production: Alembic migrations from day one of
the Postgres switch.
