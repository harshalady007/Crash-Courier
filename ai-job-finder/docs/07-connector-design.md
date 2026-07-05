# Job-Source Connector Design

## Contract

Every source is one file in `app/connectors/` implementing:

```python
class JobConnector(ABC):
    id: str                     # "remoteok"
    name: str                   # "RemoteOK"
    required_config: list[str]  # env keys, [] if keyless

    @property
    def enabled(self) -> bool   # all required_config present

    async def search(self, query: SearchQuery, client: httpx.AsyncClient) -> list[JobPosting]
```

`SearchQuery` = `{keywords: list[str], location: str | None, remote_only: bool, limit: int}`.
`JobPosting` = normalized dataclass (title, company, location, remote, description, url,
salary, posted_at, source, experience_required). Connectors never touch the DB or scorer.

## Registry

`registry.py` instantiates all connectors; `search_service` filters to `.enabled`, runs them
with `asyncio.gather(return_exceptions=True)` + per-connector timeout (12 s), logs failures
into run stats, and deduplicates by `norm(title)::norm(company)`.

## Source matrix

| Connector | Access method | Auth | Legal basis | Status |
|---|---|---|---|---|
| **RemoteOK** | `https://remoteok.com/api` JSON | none | public API, attribution requested | MVP, keyless |
| **Arbeitnow** | `https://www.arbeitnow.com/api/job-board-api` | none | public API | MVP, keyless |
| **Greenhouse boards** | `https://boards-api.greenhouse.io/v1/boards/{co}/jobs` | none | documented public API | MVP, keyless (configurable company list) |
| **Lever boards** | `https://api.lever.co/v0/postings/{co}` | none | documented public API | MVP, keyless (configurable company list) |
| **Adzuna** | official REST API | `ADZUNA_APP_ID`, `ADZUNA_APP_KEY` (free tier) | official API, covers India/US/UK/… | MVP, key-gated |
| **Jooble** | official REST API | `JOOBLE_API_KEY` (free) | official API | MVP, key-gated |
| **JSearch (RapidAPI)** | REST | `RAPIDAPI_KEY` | licensed aggregator of Google-for-Jobs — surfaces LinkedIn/Indeed/Glassdoor postings with direct apply links | MVP, key-gated |
| Naukri | — | — | no public API; HTML scraping prohibited by ToS | stub, disabled |
| Internshala | — | — | no public API | stub, disabled |
| Cutshort | — | — | no public API | stub, disabled |
| Wellfound | — | — | API is partner-only | stub, disabled |

**Why this satisfies "search LinkedIn/Indeed/Glassdoor":** those boards' postings are
indexed by Google for Jobs; JSearch licenses that index, so their listings (with direct
apply URLs back to the original site) arrive without violating any ToS.

## Per-connector rules

1. **Timeouts:** 12 s hard cap; single retry on 5xx only.
2. **Rate limiting:** stay far below documented limits; scheduler spaces daily runs.
3. **robots.txt / ToS:** connectors only call documented API endpoints — never HTML pages.
4. **Normalization:** strip HTML from descriptions, coerce dates to UTC datetimes, map
   source-specific "remote" flags.
5. **Failure isolation:** raise nothing to callers; return `[]` and let the wrapper record
   the exception in run stats.

## Adding a connector (checklist)

1. Create `app/connectors/<id>.py`, subclass `JobConnector`, implement `search()`.
2. Add required env keys to `.env.example` and `config.py`.
3. Register in `registry.py`.
4. Add a fixture-based unit test with a canned API response.
