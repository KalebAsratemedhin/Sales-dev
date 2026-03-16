import os
from glob import glob
from pathlib import Path

import requests

from core.models import OutreachConfig
from core.rag import search_chroma


def _docs_base_dir() -> Path:
    try:
        config = _get_config()
        if config.product_docs_path:
            return Path(config.product_docs_path)
    except Exception:
        pass
    base = os.environ.get("PRODUCT_DOCS_PATH") or os.environ.get("CHROMA_PERSIST_DIR")
    if base:
        return Path(base)
    return Path(__file__).resolve().parents[2] / "docs"


def search_product_docs(query: str, max_results: int = 5) -> list[dict]:
    try:
        config = _get_config()
        collection_name = (config.chroma_collection_name or "product_docs").strip() or "product_docs"
    except Exception:
        collection_name = "product_docs"
    chroma_results = search_chroma(query, collection_name=collection_name, n_results=max_results)
    if chroma_results:
        return [{"path": r.get("path", ""), "score": r.get("score", 1), "snippet": r.get("snippet", "")} for r in chroma_results]
    base_dir = _docs_base_dir()
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


def get_calendly_link(lead_email: str | None = None) -> str:
    try:
        config = _get_config()
        if config.calendly_scheduling_url:
            return config.calendly_scheduling_url.strip()
    except Exception:
        pass
    if os.environ.get("CALENDLY_SCHEDULING_LINK"):
        return os.environ["CALENDLY_SCHEDULING_LINK"]
    token = os.environ.get("CALENDLY_API_TOKEN")
    if not token:
        return ""
    try:
        resp = requests.get(
            "https://api.calendly.com/users/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("resource", {}).get("scheduling_url", "") or ""
    except requests.RequestException:
        return ""
