# Frontend Pages & Components

MVP is a single-page dashboard (React + Vite + TypeScript, no router needed) with four
stacked sections that unlock progressively. Production adds routing + auth (docs/08).

## Sections / components

### 1. UploadCard (`components/UploadCard.tsx`)
- Drag-and-drop / file picker for PDF/DOCX → `POST /api/resumes`.
- After parse: editable summary (name, skills chips, education, experience years).
- "Looks right → Analyze roles" button → `POST /api/resumes/{id}/analyze`.

### 2. RoleFitPanel (`components/RoleFitPanel.tsx`)
- Horizontal cards per role: score ring, matched/missing skill chips, explanation.
- Role cards are toggleable — selected roles seed the search query.
- "Search jobs" button with location input + remote-only toggle → `POST /api/search`.

### 3. FiltersBar (`components/FiltersBar.tsx`)
- Min-score slider, remote-only, fresher-only, internship / full-time, posted-within
  (24h/7d/30d), location text, sort by score/date. Debounced → `GET /api/jobs`.

### 4. JobsTable (`components/JobsTable.tsx`)
- Ranked rows: score badge (color by band), title+company, location/remote chip,
  experience, matched vs missing skills, source tag, posted date, **Apply** link
  (opens source URL in new tab).
- Row expand → detail: full description, component score breakdown bars,
  "Generate application kit" → `POST /api/jobs/{id}/recommend` → cover letter +
  LinkedIn message with copy buttons, priority badge.

### 5. AutomationCard
- "Run this search daily" toggle + optional email → `POST /api/automation/schedules`.

## State model
Single `App.tsx` holds: `resume`, `roleFits`, `searchStats`, `matches`, `filters`.
Plain `fetch` wrapper in `src/api.ts`; no state library needed at this size.

## Production page map (Next.js)
| Route | Page |
|---|---|
| `/` | landing + login |
| `/dashboard` | jobs table (default) |
| `/resume` | upload + parsed editor |
| `/roles` | role-fit explorer |
| `/automation` | schedules + run history |
| `/settings` | API keys, email, sources on/off |
