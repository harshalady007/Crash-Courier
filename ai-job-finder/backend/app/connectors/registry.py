"""Connector registry — the single place new sources are wired in."""
from __future__ import annotations

from ..config import Settings
from .adzuna import AdzunaConnector
from .arbeitnow import ArbeitnowConnector
from .base import DisabledStubConnector, JobConnector
from .greenhouse import GreenhouseConnector
from .jooble import JoobleConnector
from .jsearch import JSearchConnector
from .lever import LeverConnector
from .remoteok import RemoteOKConnector


class NaukriStub(DisabledStubConnector):
    id = "naukri"
    name = "Naukri"


class InternshalaStub(DisabledStubConnector):
    id = "internshala"
    name = "Internshala"


class CutshortStub(DisabledStubConnector):
    id = "cutshort"
    name = "Cutshort"


class WellfoundStub(DisabledStubConnector):
    id = "wellfound"
    name = "Wellfound"
    reason = "API is partner-only; no public access."


def build_connectors(settings: Settings) -> list[JobConnector]:
    return [
        RemoteOKConnector(settings),
        ArbeitnowConnector(settings),
        GreenhouseConnector(settings),
        LeverConnector(settings),
        AdzunaConnector(settings),
        JoobleConnector(settings),
        JSearchConnector(settings),
        NaukriStub(settings),
        InternshalaStub(settings),
        CutshortStub(settings),
        WellfoundStub(settings),
    ]
