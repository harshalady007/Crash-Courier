# Resume-Matching Algorithm

Two deterministic scorers share one skills taxonomy. All scores are 0–100 and decompose
into visible components — no opaque LLM numbers.

## 0. Skills taxonomy (`app/data/skills_taxonomy.json`)

Canonical skill ids with aliases and categories:

```json
{"id": "python", "aliases": ["python3", "py"], "category": "language"}
```

Matching = case-insensitive word-boundary regex over resume text / job description.
Aliases map to the canonical id, so "PyTorch" in a resume matches "torch" in a posting.

## 1. Role-fit score (resume → role)

Role profiles (`app/data/role_profiles.json`) define per role:
`core_skills` (must-have), `bonus_skills` (nice-to-have), `keywords` (domain phrases),
`titles` (query strings for job search).

```
role_score = 100 * (0.60 * core_coverage        # matched core / total core
                  + 0.25 * bonus_coverage       # matched bonus / total bonus
                  + 0.15 * keyword_coverage)    # keyword hits / total keywords
```

Explanation string is assembled from the actual matches:
`"Matches 5/7 core skills (python, sql, pandas, numpy, statistics); missing: excel, tableau."`

## 2. Job-match score (resume × job posting)

| Component | Weight | Computation |
|---|---|---|
| **skills** | 0.40 | Jaccard-style: matched required skills / required skills found in posting. If the posting lists no recognizable skills, fall back to overlap of resume skills with description tokens, capped at 60. |
| **title** | 0.20 | Best fuzzy/substring alignment between posting title and (a) top role-fit titles, (b) resume target roles. Exact role word hit = 100; partial (e.g. "analyst") = 60; none = 20. |
| **experience** | 0.15 | Fresher eligibility: posting signals ("fresher", "0-1", "entry level", "intern", "graduate", "junior") vs. resume experience_years. Fresher-friendly posting + ≤2 yrs resume = 100; posting demands > resume years + 1 = scaled down to 10. Unknown = 50. |
| **location** | 0.10 | Remote posting or user wants remote = 100 when compatible; city/country substring match = 100; same-country heuristic = 70; mismatch = 30; unknown = 50. |
| **recency** | 0.10 | ≤24h = 100, ≤7d = 85, ≤30d = 60, older = 30, unknown = 50. |
| **source bonus** | 0.05 | Direct company boards (greenhouse/lever) = 100 (application usually reviewed by the company itself); aggregators = 70. |

```
score = round(Σ component_score * weight)
```

### Derived fields

- **missing_skills** = posting required skills − resume skills (canonical ids).
- **shortlist_chance**: score ≥ 75 → High; ≥ 55 → Medium; else Low. Downgraded one band
  if experience component < 40 (hard experience mismatch dominates real outcomes).
- **application_difficulty**: Low if fresher_friendly and ≤3 missing skills; High if
  >5 missing skills or posting demands 3+ years; else Medium.
- **why_apply** (deterministic one-liner): built from the two strongest components,
  e.g. "Strong skills overlap (4/5 required) and fresher-friendly posting."

## 3. Experience-years estimation (parser)

Sum of date ranges found in the experience section (`Jan 2023 – Mar 2024` → 1.2y),
falling back to phrases like "X years of experience". Internships count at 0.5 weight.
Result stored as `resume.experience_years`.

## 4. Fresher-eligibility detection (posting side)

Regex over title + description:
`fresher|freshers|entry[- ]level|0[- ]?[12] year|no experience|recent graduate|intern(ship)?|graduate (trainee|engineer|program)|junior`
→ `fresher_friendly = True`. Explicit demands (`(\d+)\+? years`) extracted as
`experience_required` and used by the experience component.

## 5. Why deterministic?

- Sortable, reproducible, unit-testable (see `backend/tests/`).
- Free and instant — scoring hundreds of postings per search with an LLM would be slow
  and costly.
- The LLM layer (recommender) *reads* these components to write better prose, and can
  be upgraded later to a re-ranker over the top N without changing the contract.

## 6. Production upgrades

1. Embedding similarity (resume text ↔ job description) as a 7th component.
2. Learning-to-rank from user feedback (applied / shortlisted labels).
3. LLM re-rank of top-30 with structured output, blended 70/30 with deterministic score.
