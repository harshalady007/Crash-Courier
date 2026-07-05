# Product Requirements Document — AI Job Application Finder

**Version:** 1.0 · **Status:** MVP in development · **Audience:** Freshers / early-career candidates (0–2 years experience)

## 1. Problem Statement

Freshers spend hours manually searching multiple job boards, guessing which roles match their
resume, and applying to jobs where they have little chance of being shortlisted. There is no
single tool that (a) understands a candidate's resume, (b) searches many sources legally,
(c) scores each job for *realistic* shortlisting chances, and (d) produces the application
assets (cover letter, recruiter message) needed to apply well.

## 2. Goals

| # | Goal | Success metric |
|---|------|----------------|
| G1 | Parse any PDF/DOCX resume into structured data | ≥95% of resumes yield name + skills + education |
| G2 | Recommend best-fit roles with explainable 0–100 scores | User agrees with top-3 roles ≥80% of the time |
| G3 | Aggregate jobs from multiple legal sources | ≥4 live connectors in MVP, ≥8 in production |
| G4 | Score every job for resume match | Every job row shows score + component breakdown + missing skills |
| G5 | One-click application assets | Cover letter + recruiter message generated per job |
| G6 | Daily automated re-search with email digest | Saved search runs daily without user action |

## 3. Non-Goals (v1)

- Auto-submitting applications on the user's behalf (ToS + ethics risk).
- Scraping sites that prohibit it (LinkedIn, Naukri, Glassdoor, Indeed HTML scraping).
- Multi-user SaaS billing (single-user / self-hosted first; multi-tenant later).

## 4. Personas

1. **Priya, final-year B.Tech (CS)** — wants Data Analyst / ML intern roles in Bengaluru or remote;
   has Python, SQL, Pandas projects; no work experience.
2. **Arjun, bootcamp graduate** — junior software engineer roles; needs help writing cover letters.

## 5. Functional Requirements

### FR-1 Resume Upload & Parsing
- Accept PDF and DOCX up to 10 MB.
- Extract raw text; parse into: name, email, phone, education, skills, projects,
  experience/internships, certifications, tools/technologies, target roles (if stated).
- Show the parsed result for user confirmation/edit before searching.

### FR-2 Resume Analysis (Role Fit)
- Score the resume against a role library (Data Analyst, AI Engineer Intern, Data Scientist
  Fresher, ML Intern, Python Developer, Junior Software Engineer, Business Analyst,
  Automation Engineer, + extensible).
- Each role gets a 0–100 fit score with a human-readable explanation
  ("You match 7/9 core skills: Python, SQL, …; missing: Tableau, Excel").

### FR-3 Job Search
- Fan out queries (role titles + resume keywords + location) to all enabled connectors.
- Sources (legal access only): Adzuna API, Jooble API, JSearch (RapidAPI, aggregates
  Google-for-Jobs incl. LinkedIn/Indeed/Glassdoor listings), RemoteOK API, Arbeitnow API,
  Greenhouse & Lever public board APIs (company career pages). Naukri / Internshala /
  Cutshort ship as disabled stubs until official API access exists.
- Deduplicate across sources by normalized (title, company).

### FR-4 Job Matching Score (0–100)
Weighted components (see docs/06): skills match, title/role alignment, experience &
fresher eligibility, location match, recency, plus derived fields: missing skills,
application difficulty, shortlisting-chance label (High/Medium/Low).

### FR-5 Results Dashboard
Table columns: title, company, location/remote, experience required, skills, match score,
why apply, missing skills, direct apply link, source, posted date. Row click → detail panel.

### FR-6 Filters
Role type, location text, remote-only, fresher-only, internship, full-time, minimum match
score, posted-within (24h / 7d / 30d).

### FR-7 AI Recommendations (per job)
- Why-this-fits summary (2–3 sentences).
- Resume keywords to add.
- Tailored cover letter (~250 words).
- LinkedIn message to recruiter (≤300 chars).
- Application priority High/Medium/Low.
- Powered by Claude (`claude-opus-4-8` by default) with a deterministic template
  fallback when no API key is configured — the app must work offline/keyless.

### FR-8 Automation
- Save resume + search preferences.
- Daily scheduled re-search (APScheduler in-process; cron in production).
- Optional email digest of new jobs above the score threshold (SMTP config).

## 6. Non-Functional Requirements

- **Legality:** only official APIs / documented-public endpoints; per-connector rate limits;
  robots.txt respected for any fetch; no login-walled scraping.
- **Resilience:** one failing connector never fails the whole search (gather with per-source
  timeout + error isolation).
- **Explainability:** every score decomposes into visible components.
- **Privacy:** resume stays in the user's own DB; no third-party upload except chosen LLM API.
- **Performance:** full multi-source search < 20 s p95; parse < 3 s.
- **Extensibility:** adding a connector = one file implementing `JobConnector`.

## 7. Rollout

- **MVP (this repo):** single user, SQLite, FastAPI + React (Vite), 5+ connectors, heuristic
  parsing + optional LLM extraction, template-fallback recommendations, in-process scheduler.
- **Production (docs/08):** Postgres, auth (multi-user), Redis queue for searches, LLM resume
  parsing by default, email service, observability, Docker + Vercel/Render deploy.
