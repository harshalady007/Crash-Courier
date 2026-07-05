"""Vercel serverless entry point for the AI Job Finder FastAPI backend.

Vercel's Python runtime detects the ASGI `app` variable and serves it.
All /api/* requests are rewritten here (see vercel.json); FastAPI's own
/api-prefixed routes then match the original request path.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-job-finder", "backend"))

from app.main import app  # noqa: E402,F401
