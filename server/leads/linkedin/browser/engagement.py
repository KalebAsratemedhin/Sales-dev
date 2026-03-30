import logging
import re
import time
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from selenium.webdriver.common.by import By

from linkedin.core.constants import FEED_UPDATE_TEMPLATE, LINKEDIN_ORIGIN, SESSION_REQUIRED_MSG
from linkedin.core.post_urn import activity_urn_from_post_url, activity_id_from_urn
from linkedin.core.session import load_cookies
from linkedin.browser.driver import create_driver

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PostEngagementScrape:
    """Result of loading a post and scraping engager profile URLs."""

    post_url: str
    all_profile_urls: list[str]
    comment_profile_urls: list[str]


def _post_url_from_input(post_input: str) -> str | None:
    post_input = (post_input or "").strip()
    if not post_input:
        return None
    if post_input.startswith("http://") or post_input.startswith("https://"):
        if "linkedin.com" in post_input and ("/feed/" in post_input or "/posts/" in post_input):
            return post_input
    urn = activity_urn_from_post_url(post_input)
    if not urn:
        return None
    activity_id = activity_id_from_urn(urn)
    if not activity_id:
        return None
    return FEED_UPDATE_TEMPLATE.format(activity_id=activity_id)


def _inject_cookies(driver) -> bool:
    cookies = load_cookies()
    if not cookies:
        return False
    for c in cookies:
        try:
            cookie = {"name": c["name"], "value": c["value"]}
            if c.get("domain"):
                cookie["domain"] = c["domain"]
            if c.get("path"):
                cookie["path"] = c["path"]
            driver.add_cookie(cookie)
        except Exception:
            continue
    return True


def prepare_driver_for_linkedin(driver) -> bool:
    logger.info("Preparing driver: navigating to %s", LINKEDIN_ORIGIN)
    driver.get(LINKEDIN_ORIGIN)
    time.sleep(1.0)
    ok = _inject_cookies(driver)
    if ok:
        logger.info("Session cookies injected successfully")
    else:
        logger.warning("No cookies to inject or injection failed")
    return ok


def load_post_and_get_engagement_urls(
    driver,
    post_input: str,
    *,
    page_load_wait_sec: float = 5.0,
    scroll_pause_sec: float = 1.0,
) -> PostEngagementScrape:
    post_url = _post_url_from_input(post_input)
    if not post_url:
        logger.warning("Could not resolve post URL from input: %r", post_input)
        return PostEngagementScrape(post_url="", all_profile_urls=[], comment_profile_urls=[])
    logger.info("Loading post: %s", post_url)
    try:
        driver.get(post_url)
        time.sleep(page_load_wait_sec)
    except Exception as e:
        logger.warning("Post page load failed: %s", e)
        return PostEngagementScrape(post_url=post_url, all_profile_urls=[], comment_profile_urls=[])
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_sec)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)
    except Exception as e:
        logger.debug("Scroll failed: %s", e)
    try:
        all_urls, comment_urls = _scrape_post_engagement_lists(driver)
    except Exception as e:
        logger.warning("Scrape engagement URLs failed: %s", e)
        return PostEngagementScrape(post_url=post_url, all_profile_urls=[], comment_profile_urls=[])
    logger.info(
        "Scraped %d engagement profile URL(s) (%d from comments) from post page",
        len(all_urls),
        len(comment_urls),
    )
    return PostEngagementScrape(
        post_url=post_url,
        all_profile_urls=all_urls,
        comment_profile_urls=comment_urls,
    )


def _normalize_profile_url(href: str) -> str | None:
    if not href or "/in/" not in href:
        return None
    parsed = urlparse(href)
    path = (parsed.path or "").strip().rstrip("/")
    if "/in/" not in path:
        return None
    parts = path.split("/in/", 1)
    if len(parts) != 2:
        return None
    slug = (parts[1].split("/")[0] or "").strip()
    if not slug or len(slug) > 128:
        return None
    if re.match(r"^(ac|pub|feed|posts|company)\b", slug, re.I):
        return None
    return urljoin(LINKEDIN_ORIGIN, f"/in/{slug}/")


def _get_profile_urls_from_element(element, exclude_urls: set[str]) -> list[str]:
    try:
        links = element.find_elements(By.CSS_SELECTOR, "a[href*='/in/']")
    except Exception as e:
        logger.debug("Find links in element failed: %s", e)
        return []
    out = []
    seen = set()
    for el in links:
        try:
            href = el.get_attribute("href")
        except Exception:
            continue
        url = _normalize_profile_url(href or "")
        if url and url not in seen and url not in exclude_urls:
            seen.add(url)
            out.append(url)
    return out


def _get_post_author_url(driver) -> str | None:
    for selector in [".feed-shared-update-v2", "[data-urn*='activity']", "article.feed-shared-update-v2", ".scaffold-feed-post"]:
        try:
            containers = driver.find_elements(By.CSS_SELECTOR, selector)
            for container in containers[:2]:
                urls = _get_profile_urls_from_element(container, set())
                if urls:
                    return urls[0]
        except Exception as e:
            logger.debug("Post author selector %r failed: %s", selector, e)
            continue
    return None


def _get_comment_containers(driver) -> list:
    containers = []
    for sel in [
        ".feed-shared-comments__list",
        ".comments-comments-list",
        "[data-control-name='comments_section']",
        "section.comments-section",
        "div[class*='comments']",
        ".feed-shared-comments",
    ]:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            for el in els[:3]:
                if el not in containers:
                    containers.append(el)
            if containers:
                break
        except Exception as e:
            logger.debug("Comment selector %r failed: %s", sel, e)
            continue
    return containers


def _get_reaction_containers(driver) -> list:
    containers = []
    for sel in [
        ".social-details-reactors",
        "[data-control-name='reaction']",
        "div[class*='reactors']",
        "div[class*='reaction']",
        ".social-details-social-counts__reactions",
    ]:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            for el in els[:3]:
                if el not in containers:
                    containers.append(el)
            if containers:
                break
        except Exception as e:
            logger.debug("Reaction selector %r failed: %s", sel, e)
            continue
    return containers


def _urls_from_containers(containers: list, exclude: set[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for container in containers:
        for url in _get_profile_urls_from_element(container, exclude):
            if url not in seen:
                seen.add(url)
                out.append(url)
    return out


def _dedupe_preserve_order(*url_lists: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for lst in url_lists:
        for url in lst:
            if url not in seen:
                seen.add(url)
                out.append(url)
    return out


def _scrape_post_engagement_lists(driver) -> tuple[list[str], list[str]]:
    """Returns (all_profile_urls, comment_profile_urls)."""
    exclude: set[str] = set()
    author_url = _get_post_author_url(driver)
    if author_url:
        exclude.add(author_url)
    comment_containers = _get_comment_containers(driver)
    reaction_containers = _get_reaction_containers(driver)
    comment_urls = _urls_from_containers(comment_containers, exclude)
    reaction_urls = _urls_from_containers(reaction_containers, exclude)
    if comment_urls or reaction_urls:
        all_urls = _dedupe_preserve_order(comment_urls, reaction_urls)
        return all_urls, comment_urls
    try:
        for sel in ["main", "[role='main']", ".scaffold-layout__main", ".feed-shared-update-v2"]:
            mains = driver.find_elements(By.CSS_SELECTOR, sel)
            for main in mains[:2]:
                urls = _get_profile_urls_from_element(main, exclude)
                if urls:
                    if author_url and urls and urls[0] == author_url:
                        merged = list(dict.fromkeys(urls[1:]))
                    else:
                        merged = list(dict.fromkeys(urls))
                    return merged, []
    except Exception as e:
        logger.debug("Fallback main scrape failed: %s", e)
    return [], []


def get_engagement_profile_urls_via_browser(
    post_input: str,
    *,
    headless: bool = True,
    page_load_wait_sec: float = 5.0,
    scroll_pause_sec: float = 1.0,
) -> list[str]:
    if not load_cookies():
        raise RuntimeError(SESSION_REQUIRED_MSG)
    driver = create_driver(headless=headless)
    try:
        if not prepare_driver_for_linkedin(driver):
            logger.warning("prepare_driver_for_linkedin returned False")
            return []
        scrape = load_post_and_get_engagement_urls(
            driver,
            post_input,
            page_load_wait_sec=page_load_wait_sec,
            scroll_pause_sec=scroll_pause_sec,
        )
        return scrape.all_profile_urls
    finally:
        driver.quit()
