"""Adzuna — official REST API (free tier). Requires ADZUNA_APP_ID / ADZUNA_APP_KEY.

Docs: https://developer.adzuna.com/ — country set via ADZUNA_COUNTRY (in, us, gb, …).
"""
from __future__ import annotations

from datetime import datetime, timezone

import httpx

from .base import JobConnector, JobPosting, SearchQuery, strip_html


class AdzunaConnector(JobConnector):
    id = "adzuna"
    name = "Adzuna"
    required_config = ["ADZUNA_APP_ID", "ADZUNA_APP_KEY"]

    async def search(self, query: SearchQuery, client: httpx.AsyncClient) -> list[JobPosting]:
        country = self.settings.adzuna_country
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
        params = {
            "app_id": self.settings.adzuna_app_id,
            "app_key": self.settings.adzuna_app_key,
            "results_per_page": min(query.limit, 50),
            "what_or": " ".join(query.keywords[:8]),
            "max_days_old": 30,
            "content-type": "application/json",
        }
        if query.location:
            params["where"] = query.location

        resp = await client.get(url, params=params)
        resp.raise_for_status()

        postings: list[JobPosting] = []
        for item in resp.json().get("results", []):
            posted_at = None
            if item.get("created"):
                try:
                    posted_at = datetime.fromisoformat(item["created"].replace("Z", "+00:00"))
                    if posted_at.tzinfo is None:
                        posted_at = posted_at.replace(tzinfo=timezone.utc)
                except ValueError:
                    pass
            salary = None
            if item.get("salary_min") and item.get("salary_max"):
                salary = f"{int(item['salary_min']):,} – {int(item['salary_max']):,}"
            postings.append(JobPosting(
                title=(item.get("title") or "").strip(),
                company=(item.get("company", {}) or {}).get("display_name", ""),
                url=item.get("redirect_url", ""),
                source=self.id,
                location=(item.get("location", {}) or {}).get("display_name", ""),
                remote="remote" in (item.get("title", "") + item.get("description", "")).lower(),
                description=strip_html(item.get("description", ""))[:4000],
                salary=salary,
                posted_at=posted_at,
            ))
        return postings
