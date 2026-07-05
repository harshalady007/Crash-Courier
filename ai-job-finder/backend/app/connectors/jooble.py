"""Jooble — official REST API (free key at https://jooble.org/api/about)."""
from __future__ import annotations

from datetime import datetime, timezone

import httpx

from .base import JobConnector, JobPosting, SearchQuery, strip_html


class JoobleConnector(JobConnector):
    id = "jooble"
    name = "Jooble"
    required_config = ["JOOBLE_API_KEY"]

    async def search(self, query: SearchQuery, client: httpx.AsyncClient) -> list[JobPosting]:
        url = f"https://jooble.org/api/{self.settings.jooble_api_key}"
        payload: dict = {"keywords": " ".join(query.keywords[:6]), "page": 1}
        if query.location:
            payload["location"] = query.location

        resp = await client.post(url, json=payload)
        resp.raise_for_status()

        postings: list[JobPosting] = []
        for item in resp.json().get("jobs", [])[: query.limit]:
            posted_at = None
            if item.get("updated"):
                try:
                    posted_at = datetime.fromisoformat(item["updated"])
                    if posted_at.tzinfo is None:
                        posted_at = posted_at.replace(tzinfo=timezone.utc)
                except ValueError:
                    pass
            postings.append(JobPosting(
                title=(item.get("title") or "").strip(),
                company=(item.get("company") or "").strip(),
                url=item.get("link", ""),
                source=self.id,
                location=item.get("location", ""),
                remote="remote" in (item.get("title", "") + item.get("location", "")).lower(),
                description=strip_html(item.get("snippet", ""))[:4000],
                salary=item.get("salary") or None,
                posted_at=posted_at,
            ))
        return postings
