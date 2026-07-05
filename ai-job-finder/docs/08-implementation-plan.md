# Implementation Plan — MVP → Production

## Phase 0 — Foundations (day 1) ✅ in this repo
- Repo layout (`backend/`, `frontend/`, `docs/`), FastAPI skeleton, SQLite via SQLAlchemy,
  config from env, health endpoint, CORS for the Vite dev server.

## Phase 1 — Resume pipeline (days 2–4) ✅
- PDF (PyMuPDF) + DOCX (python-docx) text extraction.
- Heuristic section parser (contact, education, skills, projects, experience, certifications).
- Skills taxonomy + extractor; experience-years estimator.
- `POST /api/resumes`, `PATCH` for user corrections, unit tests.

## Phase 2 — Role analysis (day 5) ✅
- Role profile library (8 fresher roles) + role_scorer.
- `POST /api/resumes/{id}/analyze`, explanations, tests.

## Phase 3 — Connectors & search (days 6–9) ✅
- Connector base + registry; RemoteOK, Arbeitnow, Greenhouse, Lever (keyless);
  Adzuna, Jooble, JSearch (key-gated); disabled stubs for Naukri/Internshala/Cutshort/Wellfound.
- search_service: fan-out, dedup, persistence, run stats.

## Phase 4 — Matching & dashboard API (days 10–12) ✅
- match_scorer with weighted components, fresher detection, missing skills,
  shortlist chance, difficulty; `GET /api/jobs` filters; tests.

## Phase 5 — Frontend (days 13–16) ✅
- Vite React TS dashboard: UploadCard → RoleFitPanel → FiltersBar + JobsTable →
  detail expansion with score breakdown and application kit.

## Phase 6 — AI recommendations (day 17) ✅
- `services/llm.py` (Anthropic SDK, `claude-opus-4-8` default, env-overridable).
- recommender with template fallback; `POST /api/jobs/{id}/recommend`.

## Phase 7 — Automation (day 18) ✅
- SavedSearch CRUD, APScheduler daily job, optional SMTP digest, run history.

## Phase 8 — Hardening (days 19–21)
- More parser fixtures (real anonymized resumes), connector fixtures, error budgets,
  request logging, `.env` validation on startup, README quickstarts.

---

# MVP version (what ships from this repo)

Single-user, self-hosted. SQLite. Keyless connectors work out of the box; add free API
keys to unlock Adzuna/Jooble/JSearch. Claude-powered application kits when
`ANTHROPIC_API_KEY` is set, template fallback otherwise. In-process daily scheduler.

**Run it:**
```bash
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
cd frontend && npm install && npm run dev   # proxies /api to :8000
```

# Full production version (roadmap)

| Area | Upgrade |
|---|---|
| DB | Postgres + Alembic migrations; tsvector search on descriptions |
| Auth | Multi-user (email magic link / OAuth), per-user resumes & schedules |
| Queue | Redis + RQ/Celery: searches and LLM generation off the request path |
| Scheduler | Platform cron (Render cron job / GitHub Actions) hitting a signed endpoint |
| Parsing | LLM structured-output extraction as primary, heuristics as fallback |
| Matching | Embedding similarity component; LLM re-rank of top 30; feedback loop (applied/shortlisted labels → weight tuning) |
| Email | Transactional provider (Resend/Postmark) with digest templates |
| Connectors | Official partnerships (Naukri/Internshala), per-connector circuit breakers, response caching |
| Frontend | Next.js app router, auth pages, saved views, mobile layout |
| Ops | Docker images, health/readiness probes, Sentry, structured JSON logs, rate limiting (slowapi), backups |
| Deploy | Vercel (frontend) + Render/Railway (API + worker + Postgres + Redis) |

**Deployment sketch:**
```
Vercel (Next.js) ──► Render Web Service (FastAPI, gunicorn+uvicorn)
                        ├── Render Postgres
                        ├── Render Redis
                        ├── Render Worker (RQ: search + LLM jobs)
                        └── Render Cron (daily saved searches)
```
