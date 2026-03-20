import os
import time
import logging
from glob import glob
from pathlib import Path
from typing import Any

import requests

from core.rag import search_chroma


logger = logging.getLogger("outreach_tools")

_USER_SETTINGS_CACHE: dict[int, dict[str, Any]] = {}
_USER_SETTINGS_TTL_SECONDS = 30


def _get_user_settings(user_id: int) -> dict[str, Any]:
    cached = _USER_SETTINGS_CACHE.get(user_id)
    if cached and time.time() - cached["fetched_at"] < _USER_SETTINGS_TTL_SECONDS:
        return cached["data"]

    leads_base_url = os.environ.get("LEADS_SERVICE_URL") or "http://leads:8000"
    internal_secret = os.environ.get("LEADS_SERVICE_INTERNAL_SECRET") or ""
    headers: dict[str, str] = {}
    if internal_secret:
        headers["X-Internal-Secret"] = internal_secret

    try:
        r = requests.get(
            f"{leads_base_url}/api/auth/settings/",
            params={"user_id": user_id},
            headers=headers,
            timeout=15,
        )
        if r.status_code >= 400:
            _USER_SETTINGS_CACHE[user_id] = {"fetched_at": time.time(), "data": {}}
            return {}
        data = r.json() if r.content else {}
        _USER_SETTINGS_CACHE[user_id] = {"fetched_at": time.time(), "data": data}
        return data
    except Exception:
        logger.exception("Failed to fetch leads settings for user_id=%s", user_id)
        return {}


def _docs_base_dir(user_id: int) -> Path:
    media_root = os.environ.get("MEDIA_ROOT", "/data")
    return Path(media_root) / "product_docs" / str(user_id)


def _collection_name(user_id: int) -> str:
    return f"product_docs_{user_id}"


def search_product_docs(query: str, max_results: int = 5, user_id: int = 0) -> list[dict]:
    collection_name = _collection_name(user_id)
    chroma_results = search_chroma(query, collection_name=collection_name, n_results=max_results)
    if chroma_results:
        return [{"path": r.get("path", ""), "score": r.get("score", 1), "snippet": r.get("snippet", "")} for r in chroma_results]

    base_dir = _docs_base_dir(user_id)
    if not base_dir.exists():
        return []
    terms = [t.lower() for t in query.split() if t.strip()]
    if not terms:
        return []
    matches = []
    for pattern in ("*.md", "*.txt"):
        for path_str in glob(str(base_dir / pattern)):
            path = Path(path_str)
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            lower = text.lower()
            score = sum(lower.count(term) for term in terms)
            if score > 0:
                matches.append((score, path))
    matches.sort(key=lambda item: item[0], reverse=True)
    results = []
    for score, path in matches[:max_results]:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        results.append({"path": str(path), "score": score, "snippet": text[:800]})
    return results


def get_calendly_link(user_id: int = 0) -> str:
    """Return per-user Calendly URL (via leads settings), with env fallback."""
    data = _get_user_settings(user_id)
    url = (data.get("calendly_scheduling_url") or "").strip()
    if url:
        return url
    return (os.environ.get("CALENDLY_SCHEDULING_LINK") or "").strip()
