# System Architecture

```
┌──────────────────────────────┐
│   Frontend (React + Vite)    │  Upload · Role fit · Jobs table · Filters · Assets
└──────────────┬───────────────┘
               │ REST/JSON
┌──────────────▼───────────────────────────────────────────────┐
│                    FastAPI Backend                            │
│                                                               │
│  routers/          services/                connectors/       │
│  ├ resumes    ──►  resume_parser (PDF/DOCX → sections)        │
│  │                 skill_extractor (taxonomy match)           │
│  │                 role_scorer (role-fit 0–100)               │
│  ├ jobs       ──►  search_service ──────►  registry           │
│  │                 match_scorer            ├ adzuna (API key) │
│  ├ recs       ──►  recommender ─► llm      ├ jooble (API key) │
│  └ automation ──►  scheduler (APScheduler) ├ jsearch (RapidAPI)│
│                                            ├ remoteok         │
│                                            ├ arbeitnow        │
│                                            ├ greenhouse boards│
│                                            └ lever boards     │
│                          │                                    │
│                 SQLAlchemy ORM                                │
└──────────────────────────┬────────────────────────────────────┘
                           │
                 SQLite (MVP) / PostgreSQL (prod)
```

## Layer responsibilities

| Layer | Responsibility | Never does |
|---|---|---|
| **Routers** | HTTP validation (Pydantic), status codes | business logic |
| **resume_parser** | text extraction + section parsing | scoring |
| **skill_extractor** | taxonomy-based skill/alias detection | network calls |
| **role_scorer** | resume → role-fit scores | job fetching |
| **connectors** | one source ↔ normalized `JobPosting` | scoring, persistence |
| **search_service** | fan-out, dedup, persistence orchestration | HTTP parsing per-source |
| **match_scorer** | job × resume → match breakdown | network calls |
| **recommender / llm** | cover letters, messages, explanations | scoring (scores stay deterministic) |
| **scheduler** | daily saved-search runs, email digest | request-path work |

## Key design decisions

1. **Deterministic scoring, generative text.** Scores must be reproducible and debuggable, so
   they are computed from explicit components. The LLM only writes prose (cover letter,
   why-apply) — it never invents the number the user sorts by.
2. **Connector isolation.** `search_service` runs connectors concurrently
   (`asyncio.gather(..., return_exceptions=True)`) with a per-connector timeout. A dead or
   rate-limited source logs a warning and contributes zero jobs.
3. **Config-gated connectors.** A connector is `enabled` only when its required env keys are
   present, so a fresh clone works with the keyless sources (RemoteOK, Arbeitnow,
   Greenhouse/Lever boards) immediately.
4. **LLM optional everywhere.** `services/llm.py` calls the DeepSeek API (OpenAI-compatible); if no credentials,
   `recommender` falls back to templates and the parser falls back to heuristics.
5. **Async end-to-end.** httpx.AsyncClient for connectors; FastAPI async routes; parsing runs
   in a thread pool (CPU-bound PyMuPDF).

## Data flow: "Find me jobs"

1. `POST /api/resumes` — file → text → parsed `Resume` row (+ skills, education, etc.).
2. `POST /api/resumes/{id}/analyze` — role_scorer → `RoleFit` rows (top roles + explanations).
3. `POST /api/search` — build queries from top roles + skills → registry fan-out →
   dedupe → `Job` rows → match_scorer → `JobMatch` rows → return ranked list.
4. `GET /api/jobs?filters…` — filtered/sorted matches for the dashboard.
5. `POST /api/jobs/{match_id}/recommend` — recommender → cover letter, message, priority.
6. `POST /api/automation/schedules` — saved search; scheduler re-runs daily, emails digest.

## Production topology (docs/08 for the full plan)

Frontend on Vercel → FastAPI on Render/Railway (uvicorn workers behind gunicorn) →
managed Postgres; Redis + RQ/Celery for search jobs; cron-triggered daily searches;
Sentry + structured logs; secrets in platform env vars.
