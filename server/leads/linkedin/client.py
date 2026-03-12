"""
LinkedIn REST API client: comments and reactions using session cookies.
"""

import requests
from urllib.parse import quote

from linkedin.constants import (
    LINKEDIN_API_BASE,
    LINKEDIN_VERSION,
    RESTLI_PROTOCOL_VERSION,
)
from linkedin.session import load_cookies, cookies_to_header_dict


class LinkedInAPIError(Exception):
    """Raised when the API returns an error or missing session."""
    pass


def _ensure_session():
    """Return cookie dict for API requests; raise if no valid session."""
    cookies = load_cookies()
    if not cookies:
        raise LinkedInAPIError("No LinkedIn session. Run: python manage.py linkedin_refresh_session")
    return cookies_to_header_dict(cookies)


def _headers() -> dict[str, str]:
    """Standard headers for LinkedIn REST API."""
    return {
        "LinkedIn-Version": LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": RESTLI_PROTOCOL_VERSION,
        "User-Agent": "Mozilla/5.0 (compatible; LinkedInScraper/1.0)",
    }


def get_comments(activity_urn: str) -> list[dict]:
    """
    Fetch comments on a post (share).
    activity_urn: e.g. urn:li:activity:7302346926123798528
    Returns list of comment objects; each has 'actor' (person URN) and 'message'.
    """
    cookie_dict = _ensure_session()
    encoded = quote(activity_urn, safe="")
    url = f"{LINKEDIN_API_BASE}/socialActions/{encoded}/comments"
    resp = requests.get(
        url,
        headers=_headers(),
        cookies=cookie_dict,
        timeout=30,
    )
    if resp.status_code == 401:
        raise LinkedInAPIError("LinkedIn session expired. Run: python manage.py linkedin_refresh_session")
    if resp.status_code == 403:
        raise LinkedInAPIError("LinkedIn returned 403. Session may be invalid or lack permission.")
    resp.raise_for_status()
    data = resp.json()
    elements = data.get("elements")
    return elements if isinstance(elements, list) else []


def get_reactions(activity_urn: str, sort: str = "REVERSE_CHRONOLOGICAL") -> list[dict]:
    """
    Fetch reactions on a post.
    activity_urn: e.g. urn:li:activity:7302346926123798528
    Returns list of reaction objects; each has 'created': {'actor': person URN}.
    """
    cookie_dict = _ensure_session()
    encoded = quote(activity_urn, safe="")
    url = f"{LINKEDIN_API_BASE}/reactions/(entity:{encoded})"
    params = {"q": "entity", "sort": f"(value:{sort})"}
    resp = requests.get(
        url,
        headers=_headers(),
        cookies=cookie_dict,
        params=params,
        timeout=30,
    )
    if resp.status_code == 401:
        raise LinkedInAPIError("LinkedIn session expired. Run: python manage.py linkedin_refresh_session")
    if resp.status_code == 403:
        raise LinkedInAPIError("LinkedIn returned 403. Session may be invalid or lack permission.")
    resp.raise_for_status()
    data = resp.json()
    elements = data.get("elements")
    return elements if isinstance(elements, list) else []


def person_urn_to_profile_url(urn: str) -> str:
    """Turn urn:li:person:ABC123 into a profile URL."""
    if not urn or not urn.startswith("urn:li:person:"):
        return ""
    person_id = urn.replace("urn:li:person:", "", 1)
    return f"https://www.linkedin.com/in/{person_id}/"
