"""Greenhouse public board API — company career pages.

https://boards-api.greenhouse.io/v1/boards/{board}/jobs is a documented public API.
Boards are configured via GREENHOUSE_BOARDS (comma-separated slugs).
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import httpx

from .base import JobConnector, JobPosting, SearchQuery


class GreenhouseConnector(JobConnector):
    id = "greenhouse"
    name = "Greenhouse company boards"
    required_config: list[str] = []  # keyless; board list has a default

    @property
    def boards(self) -> list[str]:
        return [b.strip() for b in self.settings.greenhouse_boards.split(",") if b.strip()]

    @property
    def enabled(self) -> bool:
        return bool(self.boards)

    async def search(self, query: SearchQuery, client: httpx.AsyncClient) -> list[JobPosting]:
        results = await asyncio.gather(
            *(self._fetch_board(board, query, client) for board in self.boards),
            return_exceptions=True,
        )
        postings: list[JobPosting] = []
        for result in results:
            if isinstance(result, list):
                postings.extend(result)
        return postings[: query.limit]

    async def _fetch_board(self, board: str, query: SearchQuery, client: httpx.AsyncClient) -> list[JobPosting]:
        url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
        resp = await client.get(url)
        resp.raise_for_status()
        keywords = [k.lower() for k in query.keywords]

        postings: list[JobPosting] = []
        for item in resp.json().get("jobs", []):
            title = item.get("title", "")
            location = (item.get("location", {}) or {}).get("name", "")
            haystack = f"{title} {location}".lower()
            if keywords and not any(k in haystack for k in keywords):
                continue
            remote = "remote" in location.lower()
            if query.remote_only and not remote:
                continue
            posted_at = None
            if item.get("updated_at"):
                try:
                    posted_at = datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
                    if posted_at.tzinfo is None:
                        posted_at = posted_at.replace(tzinfo=timezone.utc)
                except ValueError:
                    pass
            postings.append(JobPosting(
                title=title.strip(),
                company=board.replace("-", " ").title(),
                url=item.get("absolute_url", ""),
                source=self.id,
                location=location,
                remote=remote,
                posted_at=posted_at,
            ))
        return postings
