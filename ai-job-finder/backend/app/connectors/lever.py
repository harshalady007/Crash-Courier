"""Lever public postings API — company career pages.

https://api.lever.co/v0/postings/{company}?mode=json is a documented public API.
Companies configured via LEVER_BOARDS (comma-separated slugs).
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import httpx

from .base import JobConnector, JobPosting, SearchQuery, strip_html


class LeverConnector(JobConnector):
    id = "lever"
    name = "Lever company boards"
    required_config: list[str] = []

    @property
    def boards(self) -> list[str]:
        return [b.strip() for b in self.settings.lever_boards.split(",") if b.strip()]

    @property
    def enabled(self) -> bool:
        return bool(self.boards)

    @property
    def missing_config(self) -> list[str]:
        return [] if self.boards else ["LEVER_BOARDS (comma-separated company slugs)"]

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
        url = f"https://api.lever.co/v0/postings/{board}"
        resp = await client.get(url, params={"mode": "json"})
        resp.raise_for_status()
        keywords = [k.lower() for k in query.keywords]

        postings: list[JobPosting] = []
        for item in resp.json():
            title = item.get("text", "")
            location = (item.get("categories", {}) or {}).get("location", "") or ""
            haystack = f"{title} {location}".lower()
            if keywords and not any(k in haystack for k in keywords):
                continue
            remote = "remote" in f"{location} {item.get('workplaceType', '')}".lower()
            if query.remote_only and not remote:
                continue
            posted_at = None
            if item.get("createdAt"):
                posted_at = datetime.fromtimestamp(int(item["createdAt"]) / 1000, tz=timezone.utc)
            postings.append(JobPosting(
                title=title.strip(),
                company=board.replace("-", " ").title(),
                url=item.get("hostedUrl", ""),
                source=self.id,
                location=location,
                remote=remote,
                description=strip_html(item.get("descriptionPlain") or item.get("description", ""))[:4000],
                posted_at=posted_at,
            ))
        return postings
