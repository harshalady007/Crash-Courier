"""Arbeitnow — public job board API (https://www.arbeitnow.com/api/job-board-api). Keyless."""
from __future__ import annotations

from datetime import datetime, timezone

import httpx

from .base import JobConnector, JobPosting, SearchQuery, strip_html


class ArbeitnowConnector(JobConnector):
    id = "arbeitnow"
    name = "Arbeitnow"
    required_config: list[str] = []

    API_URL = "https://www.arbeitnow.com/api/job-board-api"

    async def search(self, query: SearchQuery, client: httpx.AsyncClient) -> list[JobPosting]:
        postings: list[JobPosting] = []
        keywords = [k.lower() for k in query.keywords]

        # API is paginated but unfiltered; fetch first pages and filter locally.
        for page in (1, 2):
            resp = await client.get(self.API_URL, params={"page": page})
            resp.raise_for_status()
            for item in resp.json().get("data", []):
                haystack = " ".join([
                    item.get("title", ""),
                    " ".join(item.get("tags", []) or []),
                    item.get("description", "")[:500],
                ]).lower()
                if keywords and not any(k in haystack for k in keywords):
                    continue
                if query.remote_only and not item.get("remote"):
                    continue
                posted_at = None
                if item.get("created_at"):
                    posted_at = datetime.fromtimestamp(int(item["created_at"]), tz=timezone.utc)
                postings.append(JobPosting(
                    title=item.get("title", "").strip(),
                    company=item.get("company_name", "").strip(),
                    url=item.get("url", ""),
                    source=self.id,
                    location=item.get("location", ""),
                    remote=bool(item.get("remote")),
                    description=strip_html(item.get("description", ""))[:4000],
                    posted_at=posted_at,
                ))
                if len(postings) >= query.limit:
                    return postings
        return postings
