"""Connector contract: one source ↔ normalized JobPosting list.

Connectors call documented API endpoints only (see docs/07-connector-design.md),
never touch the DB or scorers, and never raise to callers — search_service wraps
each call and records failures in run stats.
"""
from __future__ import annotations

import html
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

import httpx

TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str | None) -> str:
    if not text:
        return ""
    cleaned = html.unescape(TAG_RE.sub(" ", text)).strip()
    # Repair common double-encoded UTF-8 (mojibake) seen in some source feeds,
    # e.g. "â€™" instead of "'". Only applied when the telltale marker is present.
    if "â€" in cleaned or "Ã" in cleaned:
        try:
            repaired = cleaned.encode("cp1252", errors="ignore").decode("utf-8", errors="ignore")
            if repaired:
                cleaned = repaired
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
    return cleaned


@dataclass
class SearchQuery:
    keywords: list[str]              # role titles + top skills
    location: str | None = None
    remote_only: bool = False
    limit: int = 30


@dataclass
class JobPosting:
    title: str
    company: str
    url: str
    source: str
    location: str = ""
    remote: bool = False
    description: str = ""
    salary: str | None = None
    posted_at: datetime | None = None
    experience_required: str | None = None
    raw: dict = field(default_factory=dict, repr=False)


class JobConnector(ABC):
    id: str
    name: str
    required_config: list[str] = []

    def __init__(self, settings) -> None:
        self.settings = settings

    @property
    def missing_config(self) -> list[str]:
        return [key for key in self.required_config if not getattr(self.settings, key.lower(), None)]

    @property
    def enabled(self) -> bool:
        return not self.missing_config

    @abstractmethod
    async def search(self, query: SearchQuery, client: httpx.AsyncClient) -> list[JobPosting]:
        """Fetch and normalize postings. May raise — the caller isolates failures."""


class DisabledStubConnector(JobConnector):
    """Placeholder for sources without legal API access (Naukri, Internshala, …).

    Kept in the registry so /api/sources documents why they're off.
    """

    reason: str = "No official public API; scraping prohibited by the site's terms of service."

    @property
    def enabled(self) -> bool:
        return False

    @property
    def missing_config(self) -> list[str]:
        return [f"unavailable: {self.reason}"]

    async def search(self, query: SearchQuery, client: httpx.AsyncClient) -> list[JobPosting]:
        return []
