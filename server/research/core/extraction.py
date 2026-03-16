import os
from urllib.parse import urljoin, urlparse

import trafilatura

from core.utils import fetch_url_with_retries, simple_extract_text

DEFAULT_MAX_CHARS = 20000
DEFAULT_MAX_EXTRA_PAGES = 2
DEFAULT_MAX_TOTAL_CHARS = 50000

KEY_PATHS = ["/about", "/product", "/solutions", "/platform", "/features"]


def extract_main_content(html, url=None, max_chars=DEFAULT_MAX_CHARS):
    if not (html or "").strip():
        return ""
    try:
        text = trafilatura.extract(html, url=url or "")
    except Exception:
        text = None
    if not text or not text.strip():
        text = simple_extract_text(html, max_chars=max_chars)
    else:
        text = text.strip().replace("\n\n\n", "\n\n")[:max_chars]
    return text


def _same_origin(base_url, other_url):
    return urlparse(base_url).netloc == urlparse(other_url).netloc


def _build_candidate_urls(base_url):
    parsed = urlparse(base_url)
    base = f"{parsed.scheme or 'https'}://{parsed.netloc}".rstrip("/")
    return [urljoin(base + "/", p) for p in KEY_PATHS]


def gather_site_text(
    base_url,
    max_extra_pages=DEFAULT_MAX_EXTRA_PAGES,
    max_total_chars=DEFAULT_MAX_TOTAL_CHARS,
):
    seen = set()
    parts = []

    def add_page(url):
        if url in seen or not _same_origin(base_url, url):
            return
        seen.add(url)
        try:
            html = fetch_url_with_retries(url)
            text = extract_main_content(html, url=url, max_chars=max_total_chars)
            if text and text.strip():
                parts.append(text.strip())
        except Exception:
            pass

    add_page(base_url)
    for candidate in _build_candidate_urls(base_url):
        if len(parts) >= 1 + max_extra_pages:
            break
        add_page(candidate)

    combined = "\n\n".join(parts)
    return combined[:max_total_chars] if combined else ""
