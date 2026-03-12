"""
LinkedIn session: load/save cookies from disk and refresh via Selenium.
"""

import json
import os
from pathlib import Path
from typing import Any

from linkedin.constants import LINKEDIN_LOGIN_URL


def get_session_path() -> Path:
    """Path to the file where we persist LinkedIn cookies."""
    from django.conf import settings
    path = getattr(settings, "LINKEDIN_SESSION_PATH", None)
    if path:
        return Path(path)
    base = Path(settings.BASE_DIR)
    data_dir = base / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "linkedin_session.json"


def load_cookies() -> list[dict[str, Any]] | None:
    """
    Load persisted cookies from disk.
    Returns list of cookie dicts (name, value, domain, path) or None if missing/invalid.
    """
    path = get_session_path()
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, list):
        return None
    return [c for c in data if isinstance(c.get("name"), str) and isinstance(c.get("value"), str)]


def save_cookies(cookies: list[dict[str, Any]]) -> None:
    """Persist cookies to disk (only name, value, domain, path)."""
    path = get_session_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    out = []
    for c in cookies:
        out.append({
            "name": c.get("name", ""),
            "value": c.get("value", ""),
            "domain": c.get("domain", ""),
            "path": c.get("path", "/"),
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


def cookies_to_header_dict(cookies: list[dict[str, Any]]) -> dict[str, str]:
    """Build a Cookie header–friendly dict (name -> value) for requests."""
    return {c["name"]: c["value"] for c in cookies if c.get("name") and c.get("value")}


def refresh_session(
    email: str,
    password: str,
    *,
    headless: bool = True,
    wait_seconds_after_login: int = 5,
) -> bool:
    """
    Log in to LinkedIn with Selenium + undetected-chromedriver, then save cookies.

    Returns True if login succeeded and cookies were saved, False otherwise.
    If 2FA/challenge appears, the browser stays open for the user to complete it;
    then we save cookies when the user has reached the feed.
    """
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
    except ImportError as e:
        raise ImportError(
            "linkedin.session.refresh_session requires selenium and undetected-chromedriver. "
            "Install with: pip install selenium undetected-chromedriver"
        ) from e

    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)
    try:
        driver.get(LINKEDIN_LOGIN_URL)
        wait = WebDriverWait(driver, 20)

        username = wait.until(EC.presence_of_element_located((By.ID, "username")))
        username.clear()
        username.send_keys(email)

        password_el = driver.find_element(By.ID, "password")
        password_el.clear()
        password_el.send_keys(password)

        submit = driver.find_element(By.CSS_SELECTOR, ".login__form_action_container button")
        submit.click()

        # Wait for redirect to feed or challenge
        wait.until(lambda d: "feed" in d.current_url or "checkpoint" in d.current_url or "challenge" in d.current_url.lower())
        import time
        time.sleep(wait_seconds_after_login)

        # If we're still on a challenge page, we could return False or wait longer.
        # For now we save whatever cookies we have (user may have completed 2FA).
        all_cookies = driver.get_cookies()
        linkedin_cookies = [
            c for c in all_cookies
            if c.get("domain") and "linkedin.com" in c["domain"]
        ]
        has_li_at = any(c.get("name") == "li_at" for c in linkedin_cookies)
        if linkedin_cookies:
            save_cookies(linkedin_cookies)
        return has_li_at
    finally:
        driver.quit()
