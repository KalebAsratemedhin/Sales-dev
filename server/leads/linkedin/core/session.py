import json
import os
from pathlib import Path
from typing import Any

from linkedin.core.constants import LINKEDIN_LOGIN_URL

CHROME_BINARY_CANDIDATES = [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/snap/bin/chromium",
]


def _find_chrome_binary() -> str | None:
    path = os.environ.get("LINKEDIN_CHROME_PATH", "").strip()
    if path and os.path.isfile(path):
        return path
    for candidate in CHROME_BINARY_CANDIDATES:
        if os.path.isfile(candidate):
            return candidate
    return None


def get_session_path() -> Path:
    from django.conf import settings
    path = getattr(settings, "LINKEDIN_SESSION_PATH", None)
    if path:
        return Path(path)
    base = Path(settings.BASE_DIR)
    data_dir = base / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "linkedin_session.json"


def load_cookies() -> list[dict[str, Any]] | None:
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
    return {c["name"]: c["value"] for c in cookies if c.get("name") and c.get("value")}


def refresh_session(
    email: str,
    password: str,
    *,
    headless: bool = True,
    wait_seconds_after_login: int = 5,
) -> bool:
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
    except ImportError as e:
        raise ImportError(
            "linkedin.core.session requires selenium and undetected-chromedriver. "
            "pip install selenium undetected-chromedriver"
        ) from e
    from linkedin.browser.driver import create_driver
    driver = create_driver(headless=headless)
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
        wait.until(lambda d: "feed" in d.current_url or "checkpoint" in d.current_url or "challenge" in d.current_url.lower())
        import time
        time.sleep(wait_seconds_after_login)
        all_cookies = driver.get_cookies()
        linkedin_cookies = [c for c in all_cookies if c.get("domain") and "linkedin.com" in c["domain"]]
        has_li_at = any(c.get("name") == "li_at" for c in linkedin_cookies)
        if linkedin_cookies:
            save_cookies(linkedin_cookies)
        return has_li_at
    finally:
        driver.quit()
