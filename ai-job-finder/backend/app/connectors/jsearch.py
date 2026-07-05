"""JSearch (RapidAPI) — licensed Google-for-Jobs aggregator.

Surfaces postings from LinkedIn, Indeed, Glassdoor, etc. with direct apply links,
without scraping those sites. Requires RAPIDAPI_KEY (free tier available).
"""
from __future__ import annotations

from datetime import datetime, timezone

import httpx

from .base import JobConnector, JobPosting, SearchQuery


class JSearchConnector(JobConnector):
    id = "jsearch"
    name = "JSearch (LinkedIn/Indeed/Glassdoor via Google Jobs)"
    required_config = ["RAPIDAPI_KEY"]

    API_URL = "https://jsearch.p.rapidapi.com/search"

    async def search(self, query: SearchQuery, client: httpx.AsyncClient) -> list[JobPosting]:
        q = " OR ".join(query.keywords[:3]) or "software engineer"
        if query.location:
            q += f" in {query.location}"
        params = {
            "query": q,
            "page": "1",
            "num_pages": "1",
            "date_posted": "month",
        }
        if query.remote_only:
            params["work_from_home"] = "true"

        resp = await client.get(
            self.API_URL,
            params=params,
            headers={
                "X-RapidAPI-Key": self.settings.rapidapi_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
            },
        )
        resp.raise_for_status()

        postings: list[JobPosting] = []
        for item in resp.json().get("data", [])[: query.limit]:
            posted_at = None
            if item.get("job_posted_at_timestamp"):
                posted_at = datetime.fromtimestamp(int(item["job_posted_at_timestamp"]), tz=timezone.utc)
            location = ", ".join(
                p for p in [item.get("job_city"), item.get("job_state"), item.get("job_country")] if p
            )
            salary = None
            if item.get("job_min_salary") and item.get("job_max_salary"):
                salary = f"{item['job_min_salary']:,.0f} – {item['job_max_salary']:,.0f} {item.get('job_salary_currency') or ''}".strip()
            postings.append(JobPosting(
                title=(item.get("job_title") or "").strip(),
                company=(item.get("employer_name") or "").strip(),
                url=item.get("job_apply_link", ""),
                source=self.id,
                location=location,
                remote=bool(item.get("job_is_remote")),
                description=(item.get("job_description") or "")[:4000],
                salary=salary,
                posted_at=posted_at,
            ))
        return postings
