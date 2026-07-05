"""RemoteOK — public JSON API (https://remoteok.com/api). Keyless, remote jobs only."""
from __future__ import annotations

from datetime import datetime, timezone

import httpx

from .base import JobConnector, JobPosting, SearchQuery, strip_html


class RemoteOKConnector(JobConnector):
    id = "remoteok"
    name = "RemoteOK"
    required_config: list[str] = []

    API_URL = "https://remoteok.com/api"

    async def search(self, query: SearchQuery, client: httpx.AsyncClient) -> list[JobPosting]:
        resp = await client.get(self.API_URL, headers={"User-Agent": "ai-job-finder"})
        resp.raise_for_status()
        data = resp.json()

        keywords = [k.lower() for k in query.keywords]
        postings: list[JobPosting] = []
        for item in data:
            if not isinstance(item, dict) or "position" not in item:
                continue  # first element is a legal notice
            haystack = " ".join([
                item.get("position", ""),
                " ".join(item.get("tags", []) or []),
                item.get("description", "")[:500],
            ]).lower()
            if keywords and not any(k in haystack for k in keywords):
                continue
            posted_at = None
            if item.get("epoch"):
                posted_at = datetime.fromtimestamp(int(item["epoch"]), tz=timezone.utc)
            postings.append(JobPosting(
                title=item.get("position", "").strip(),
                company=item.get("company", "").strip(),
                url=item.get("url") or f"https://remoteok.com/l/{item.get('id', '')}",
                source=self.id,
                location=item.get("location") or "Remote",
                remote=True,
                description=strip_html(item.get("description", ""))[:4000],
                salary=self._salary(item),
                posted_at=posted_at,
            ))
            if len(postings) >= query.limit:
                break
        return postings

    @staticmethod
    def _salary(item: dict) -> str | None:
        lo, hi = item.get("salary_min"), item.get("salary_max")
        if lo and hi:
            return f"${int(lo):,} – ${int(hi):,}"
        return None
