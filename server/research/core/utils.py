import re
import time

import requests

from core.exceptions import TransientError

FETCH_RETRIES = 3
FETCH_BACKOFF_BASE = 1.0


def simple_extract_text(html, max_chars=20000):
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<[^>]+>", " ", html)
    html = re.sub(r"\s+", " ", html)
    return html.strip()[:max_chars]


def fetch_url_with_retries(url, timeout=15, retries=FETCH_RETRIES, backoff_base=FETCH_BACKOFF_BASE):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; SDRBot/1.0)"}
    last_error = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=timeout, headers=headers)
            resp.raise_for_status()
            return resp.text
        except (requests.RequestException, requests.HTTPError) as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(backoff_base * (2 ** attempt))
    raise TransientError(f"Fetch failed after {retries} attempts: {last_error}")


def run_with_retries(fn, retries=3, backoff_base=1.0, *args, **kwargs):
    last_error = None
    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except TransientError as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(backoff_base * (2 ** attempt))
    raise last_error