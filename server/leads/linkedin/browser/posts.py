import logging
import re
import time
from datetime import date, datetime, timedelta

from selenium.webdriver.common.by import By

from linkedin.core.constants import FEED_UPDATE_TEMPLATE

logger = logging.getLogger(__name__)

ACTIVITY_SCROLL_PAUSE_SEC = 1.5
ACTIVITY_LOAD_WAIT_SEC = 5


def _profile_activity_url(profile_url: str) -> str | None:
    if not profile_url:
        return None
    return profile_url.rstrip("/") + "/details/activity/"


def _extract_activity_id_from_href(href: str) -> str | None:
    if not href:
        return None
    m = re.search(r"urn:li:activity:(\d+)", href, re.I)
    if m:
        return m.group(1)
    m = re.search(r"-activity-(\d+)(?:-|/|$)", href, re.I)
    if m:
        return m.group(1)
    return None


def _parse_relative_time(text: str, reference: date | None = None) -> date | None:
    if not text:
        return None
    ref = reference or date.today()
    text = (text or "").strip().lower()
    m = re.match(r"^(\d+)\s*(min|mins?|h|hrs?|d|days?|w|wk|wks?|mo|mos?|mon|y|yrs?)\b", text)
    if not m:
        if "yesterday" in text:
            return ref - timedelta(days=1)
        if "today" in text or "just now" in text:
            return ref
        return None
    num = int(m.group(1))
    unit = m.group(2)
    if unit.startswith("min") or unit == "h":
        return ref
    if unit in ("d", "day", "days"):
        return ref - timedelta(days=num)
    if unit in ("w", "wk", "wks"):
        return ref - timedelta(weeks=num)
    if unit in ("mo", "mos", "mon"):
        return ref - timedelta(days=num * 30)
    if unit in ("y", "yr", "yrs"):
        return ref - timedelta(days=num * 365)
    return ref


def _parse_datetime_attr(dt_str: str) -> date | None:
    if not dt_str:
        return None
    try:
        if "T" in dt_str:
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).date()
        return datetime.strptime(dt_str.strip()[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def get_posts_from_profile_between_dates(
    driver,
    profile_url: str,
    start_date: date,
    end_date: date,
    *,
    max_scrolls: int = 10,
) -> list[str]:
    activity_url = _profile_activity_url(profile_url)
    if not activity_url:
        logger.warning("Invalid profile URL for activity: %s", profile_url)
        return []
    logger.info("Loading profile activity: %s", activity_url)
    try:
        driver.get(activity_url)
        time.sleep(ACTIVITY_LOAD_WAIT_SEC)
    except Exception as e:
        logger.warning("Activity page load failed: %s", e)
        return []
    try:
        current = driver.current_url
        if "/details/activity" not in current:
            driver.get(profile_url.rstrip("/"))
            time.sleep(ACTIVITY_LOAD_WAIT_SEC)
    except Exception as e:
        logger.warning("Fallback to profile URL failed: %s", e)
    for _ in range(max_scrolls):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(ACTIVITY_SCROLL_PAUSE_SEC)
        except Exception as e:
            logger.debug("Scroll failed: %s", e)
            break
    seen_ids: set[str] = set()
    post_urls: list[str] = []
    post_dates: dict[str, date] = {}
    try:
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='activity']")
    except Exception as e:
        logger.warning("Find activity links failed: %s", e)
        return []
    for el in links:
        try:
            href = el.get_attribute("href") or ""
        except Exception:
            continue
        aid = _extract_activity_id_from_href(href)
        if not aid or aid in seen_ids:
            continue
        seen_ids.add(aid)
        canonical = FEED_UPDATE_TEMPLATE.format(activity_id=aid)
        post_urls.append(canonical)
        post_date: date | None = None
        try:
            parent = el
            for _ in range(5):
                parent = parent.find_element(By.XPATH, "..")
                times = parent.find_elements(By.CSS_SELECTOR, "time[datetime]")
                for t in times:
                    dt = t.get_attribute("datetime")
                    post_date = _parse_datetime_attr(dt or "")
                    if post_date:
                        break
                if post_date:
                    break
                raw_text = (parent.text or "")[:80]
                post_date = _parse_relative_time(raw_text)
                if post_date:
                    break
        except Exception:
            pass
        if post_date:
            post_dates[aid] = post_date
    if post_dates:
        filtered = []
        for u in post_urls:
            aid = _extract_activity_id_from_href(u)
            if not aid:
                continue
            d = post_dates.get(aid)
            if d is None or (start_date <= d <= end_date):
                filtered.append(u)
        logger.info(
            "Profile activity: %d post(s) in date range %s to %s",
            len(filtered),
            start_date,
            end_date,
        )
        return filtered
    logger.info("Profile activity: %d post(s) (no dates parsed, returning all)", len(post_urls))
    return post_urls
