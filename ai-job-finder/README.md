# AI Job Finder

AI-powered job application finder for freshers / early-career candidates.
Upload a resume → get best-fit roles with explainable scores → search jobs across
multiple legal sources → see match scores, missing skills, and direct apply links →
generate a tailored cover letter + recruiter message per job → automate daily.

## Repository layout

```
ai-job-finder/
├── docs/        Product & engineering docs (PRD, architecture, schema, API, algorithm, connectors, plan)
├── backend/     FastAPI + SQLAlchemy + connectors + scoring + DeepSeek integration
└── frontend/    React (Vite + TypeScript) dashboard
```

## Quick start

**Backend** (Python 3.11+):
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # optional — works keyless out of the box
uvicorn app.main:app --reload # http://localhost:8000/docs
```

**Frontend** (Node 20+):
```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173 (proxies /api to :8000)
```

**Tests:**
```bash
cd backend && python -m pytest
```

## What works keyless

RemoteOK, Arbeitnow, and Greenhouse company boards are enabled with zero configuration.
Add free API keys in `backend/.env` to unlock:

| Key | Unlocks |
|---|---|
| `ADZUNA_APP_ID` + `ADZUNA_APP_KEY` | Adzuna (strong India/US/UK coverage) |
| `JOOBLE_API_KEY` | Jooble aggregator |
| `RAPIDAPI_KEY` | JSearch — LinkedIn/Indeed/Glassdoor postings via the licensed Google-for-Jobs index |
| `DEEPSEEK_API_KEY` | DeepSeek-generated cover letters & recruiter messages (template fallback otherwise) |
| `SMTP_*` | Daily email digests |

Naukri / Internshala / Cutshort / Wellfound have no public APIs and their ToS prohibit
scraping — they ship as documented disabled stubs (`GET /api/sources` explains each).

## Docs

1. [Product requirements](docs/01-product-requirements.md)
2. [System architecture](docs/02-system-architecture.md)
3. [Database schema](docs/03-database-schema.md)
4. [API routes](docs/04-api-routes.md)
5. [Frontend pages](docs/05-frontend-pages.md)
6. [Matching algorithm](docs/06-matching-algorithm.md)
7. [Connector design](docs/07-connector-design.md)
8. [Implementation plan + MVP → production roadmap](docs/08-implementation-plan.md)

## Principles

- **Legal-first sourcing** — official APIs and documented public endpoints only.
- **Explainable scoring** — every 0–100 score decomposes into visible weighted components;
  the LLM writes prose, never the numbers.
- **Graceful degradation** — no API keys, no LLM, one dead source: everything still works.
