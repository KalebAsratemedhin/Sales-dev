import logging
import time
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

DEFAULT_PROFILE_VISIT_DELAY_SEC = 1.5
PROFILE_LOAD_WAIT_SEC = 8
NAME_REJECT_SUBSTRINGS = ("notification", "connect", "message", "follow", "invite")


def _looks_like_person_name(raw: str) -> bool:
    if not raw or len(raw) > 120 or "\n" in raw:
        return False
    lower = raw.lower()
    for reject in NAME_REJECT_SUBSTRINGS:
        if reject in lower:
            return False
    words = raw.split()
    if not (2 <= len(words) <= 5):
        return False
    for word in words:
        if not word.replace("-", "").replace("'", "").replace(".", "").isalpha():
            return False
    return True


def get_profile_info(driver: Any, profile_url: str) -> dict[str, str | None]:
    result: dict[str, str | None] = {
        "first_name": "",
        "last_name": "",
        "email": None,
        "website": None,
    }
    logger.info("Visiting profile: %s", profile_url)
    try:
        driver.get(profile_url)
        time.sleep(1.0)
    except Exception as e:
        logger.warning("Failed to load profile %s: %s", profile_url, e)
        return result
    name_selectors = [
        "section.basic-profile-section h1.heading-large",
        "section.basic-profile-section h1",
        "h2",
        "a > h1",
        "h1.text-heading-xlarge",
        ".text-heading-xlarge",
        "h1.inline.t-24",
        "[data-anonymize='person-name']",
        "h1",
    ]
    name_text: str | None = None
    for selector in name_selectors:
        try:
            wait = WebDriverWait(driver, PROFILE_LOAD_WAIT_SEC)
            if selector == "h2":
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2")))
                for el in driver.find_elements(By.CSS_SELECTOR, "h2"):
                    raw = (el.text or "").strip()
                    if _looks_like_person_name(raw):
                        name_text = raw
                        logger.debug("Name found with selector %r: %r", selector, raw)
                        break
                if name_text:
                    break
            else:
                el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                raw = (el.text or "").strip()
                if _looks_like_person_name(raw):
                    name_text = raw
                    logger.debug("Name found with selector %r: %r", selector, raw)
                    break
        except Exception as e:
            logger.debug("Name selector %r failed: %s", selector, e)
            continue
    if not name_text:
        logger.warning("No name on profile %s (tried %d selectors)", profile_url, len(name_selectors))
        return result
    parts = name_text.split()
    if parts:
        result["first_name"] = parts[0]
        result["last_name"] = " ".join(parts[1:]) if len(parts) > 1 else ""
    logger.info("Profile name: %s %s", result["first_name"], result["last_name"])
    email_selectors = [
        "a[href^='mailto:']",
        "section a[href*='mailto']",
        "[data-anonymize='email']",
        ".ci-email a",
        ".contact-info__email",
    ]
    for selector in email_selectors:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in els:
                href = el.get_attribute("href") or ""
                if href.startswith("mailto:"):
                    addr = href.replace("mailto:", "").strip().split("?")[0].strip()
                    if addr and "@" in addr and len(addr) < 255:
                        result["email"] = addr
                        logger.info("Profile email obtained: %s", addr)
                        return result
                text = (el.text or "").strip()
                if "@" in text and " " not in text and len(text) < 255:
                    result["email"] = text
                    logger.info("Profile email obtained (from text): %s", text)
                    return result
        except Exception as e:
            logger.debug("Email selector %r failed: %s", selector, e)
            continue
    _scrape_contact_info_overlay(driver, profile_url, result)
    if not result["email"]:
        logger.debug("No email found on profile %s", profile_url)
    return result


def _scrape_contact_info_overlay(
    driver: Any, profile_url: str, result: dict[str, str | None]
) -> None:
    base = profile_url.rstrip("/")
    if "/in/" not in base:
        return
    contact_url = base + "/overlay/contact-info/"
    logger.info("Opening Contact info overlay: %s", contact_url)
    try:
        driver.get(contact_url)
        time.sleep(2.0)
    except Exception as e:
        logger.warning("Contact info overlay load failed: %s", e)
        return
    if not result.get("email"):
        for selector in ["a[href^='mailto:']", ".pv-contact-info__contact-link", "[data-anonymize='email']"]:
            try:
                els = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in els:
                    href = (el.get_attribute("href") or "").strip()
                    if href.startswith("mailto:"):
                        addr = href.replace("mailto:", "").strip().split("?")[0].strip()
                        if addr and "@" in addr and len(addr) < 255:
                            result["email"] = addr
                            logger.info("Profile email obtained from overlay: %s", addr)
                            break
                    text = (el.text or "").strip()
                    if "@" in text and " " not in text and len(text) < 255:
                        result["email"] = text
                        logger.info("Profile email obtained from overlay (text): %s", text)
                        break
                if result.get("email"):
                    break
            except Exception as e:
                logger.debug("Overlay email selector %r failed: %s", selector, e)
    try:
        for p in driver.find_elements(By.TAG_NAME, "p"):
            if (p.text or "").strip() != "Website":
                continue
            parent = p.find_element(By.XPATH, "./..")
            try:
                link_el = parent.find_element(By.CSS_SELECTOR, "a[href]")
            except Exception:
                continue
            href = (link_el.get_attribute("href") or "").strip()
            if not href or len(href) > 2048:
                continue
            if "linkedin.com/redir/redirect" in href or "linkedin.com/redir/redirect/" in href:
                parsed = urlparse(href)
                qs = parse_qs(parsed.query)
                raw = (qs.get("url") or [None])[0]
                if raw:
                    decoded = unquote(raw)
                    if decoded and not decoded.startswith("http"):
                        decoded = "https://" + decoded.lstrip("/")
                    if decoded and (decoded.startswith("http://") or decoded.startswith("https://")):
                        result["website"] = decoded
                        logger.info("Profile website obtained from overlay (redirect): %s", decoded)
                        break
            elif "linkedin.com" not in href and not href.startswith("mailto:"):
                if href.startswith("http://") or href.startswith("https://"):
                    result["website"] = href
                    logger.info("Profile website obtained from overlay: %s", href)
                    break
    except Exception as e:
        logger.warning("Overlay website scrape failed: %s", e)
