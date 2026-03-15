import requests
from urllib.parse import quote

from linkedin.core.constants import (
    LINKEDIN_API_BASE,
    LINKEDIN_VERSION,
    RESTLI_PROTOCOL_VERSION,
)
from linkedin.core.session import load_cookies, cookies_to_header_dict


class LinkedInAPIError(Exception):
    pass


def _ensure_session():
    cookies = load_cookies()
    if not cookies:
        raise LinkedInAPIError("No LinkedIn session. Run: python manage.py linkedin_refresh_session")
    return cookies_to_header_dict(cookies)


def _headers() -> dict[str, str]:
    return {
        "LinkedIn-Version": LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": RESTLI_PROTOCOL_VERSION,
        "User-Agent": "Mozilla/5.0 (compatible; LinkedInScraper/1.0)",
    }


def get_comments(activity_urn: str) -> list[dict]:
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
    if not urn or not urn.startswith("urn:li:person:"):
        return ""
    person_id = urn.replace("urn:li:person:", "", 1)
    return f"https://www.linkedin.com/in/{person_id}/"
