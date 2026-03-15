import logging
import re
import time
from datetime import date

from linkedin.browser import (
    create_driver,
    DEFAULT_PROFILE_VISIT_DELAY_SEC,
    get_posts_from_profile_between_dates,
    get_profile_info,
    load_post_and_get_engagement_urls,
    prepare_driver_for_linkedin,
)
from linkedin.core.constants import SESSION_REQUIRED_MSG
from linkedin.core.session import load_cookies

from config.models import Lead

logger = logging.getLogger(__name__)


def placeholder_email(profile_url: str) -> str:
    if not profile_url or "/in/" not in profile_url:
        slug = "unknown"
    else:
        slug = profile_url.rstrip("/").split("/")[-1] or "unknown"
    slug = re.sub(r"[^a-zA-Z0-9._-]", "-", slug)[:64]
    return f"{slug}@linkedin.placeholder"


def _build_name(info: dict) -> str:
    first = (info.get("first_name") or "").strip()
    last = (info.get("last_name") or "").strip()
    return " ".join(filter(None, [first, last])).strip()


def _lead_defaults(
    profile_url: str,
    name: str,
    email: str,
    website: str,
    persona_id: int | None,
) -> dict:
    return {
        "email": email or placeholder_email(profile_url),
        "name": name,
        "company_name": "",
        "company_website": website or "",
        "persona_id": persona_id,
        "status": Lead.Status.NEW,
    }


def _sync_leads_for_one_post(
    driver,
    post_input: str,
    *,
    persona_id: int | None = None,
    profile_visit_delay_sec: float = DEFAULT_PROFILE_VISIT_DELAY_SEC,
) -> tuple[int, int]:
    logger.info("Loading post and scraping engagement: %r", post_input)
    try:
        profile_urls = load_post_and_get_engagement_urls(driver, post_input)
    except Exception as e:
        logger.error("Failed to load engagement for post %r: %s", post_input, e)
        return 0, 0
    logger.info("Obtained %d profile URL(s) from engagement", len(profile_urls))
    created, updated = 0, 0
    for i, profile_url in enumerate(profile_urls, 1):
        if not profile_url:
            continue
        logger.info("Processing profile %d/%d: %s", i, len(profile_urls), profile_url)
        try:
            info = get_profile_info(driver, profile_url)
        except Exception as e:
            logger.warning("Failed to scrape profile %s: %s", profile_url, e)
            continue
        name = _build_name(info)
        scraped_email = (info.get("email") or "").strip()
        scraped_website = (info.get("website") or "").strip()
        logger.info("Scraped: name=%r email=%s website=%s", name or "(none)", scraped_email or "(placeholder)", scraped_website or "(none)")
        try:
            lead, was_created = Lead.objects.get_or_create(
                profile_url=profile_url,
                source=Lead.Source.LINKEDIN,
                defaults=_lead_defaults(
                    profile_url, name, scraped_email, scraped_website, persona_id
                ),
            )
        except Exception as e:
            logger.error("Failed to create/update Lead for %s: %s", profile_url, e)
            continue
        if was_created:
            created += 1
            logger.info("Lead created: id=%s profile_url=%s", lead.id, profile_url)
        else:
            lead.name = name
            update_fields = ["name"]
            if scraped_email:
                lead.email = scraped_email
                update_fields.append("email")
            if scraped_website:
                lead.company_website = scraped_website
                update_fields.append("company_website")
            try:
                lead.save(update_fields=update_fields)
            except Exception as e:
                logger.error("Failed to save Lead id=%s: %s", lead.id, e)
                continue
            updated += 1
            logger.info("Lead updated: id=%s profile_url=%s", lead.id, profile_url)
        time.sleep(profile_visit_delay_sec)
    return created, updated


def sync_leads_from_post(
    post_input: str,
    *,
    persona_id: int | None = None,
    headless: bool = True,
    profile_visit_delay_sec: float = DEFAULT_PROFILE_VISIT_DELAY_SEC,
) -> tuple[int, int]:
    logger.info("Starting sync for post_input=%r", post_input)
    if not load_cookies():
        raise RuntimeError(SESSION_REQUIRED_MSG)
    driver = create_driver(headless=headless)
    logger.info("Browser driver created (headless=%s)", headless)
    try:
        if not prepare_driver_for_linkedin(driver):
            raise RuntimeError(SESSION_REQUIRED_MSG)
        created, updated = _sync_leads_for_one_post(
            driver, post_input, persona_id=persona_id, profile_visit_delay_sec=profile_visit_delay_sec
        )
    except RuntimeError:
        raise
    except Exception as e:
        logger.error("Sync failed for post %r: %s", post_input, e)
        raise
    finally:
        try:
            driver.quit()
        except Exception as e:
            logger.warning("Driver quit failed: %s", e)
    logger.info("Sync complete: created=%d updated=%d", created, updated)
    return created, updated


def sync_leads_from_profile(
    profile_url: str,
    start_date: date,
    end_date: date,
    *,
    persona_id: int | None = None,
    headless: bool = True,
    profile_visit_delay_sec: float = DEFAULT_PROFILE_VISIT_DELAY_SEC,
    max_activity_scrolls: int = 10,
) -> tuple[int, int]:
    logger.info("Starting profile sync: %r between %s and %s", profile_url, start_date, end_date)
    if not load_cookies():
        raise RuntimeError(SESSION_REQUIRED_MSG)
    driver = create_driver(headless=headless)
    total_created, total_updated = 0, 0
    try:
        if not prepare_driver_for_linkedin(driver):
            raise RuntimeError(SESSION_REQUIRED_MSG)
        try:
            post_urls = get_posts_from_profile_between_dates(
                driver, profile_url, start_date, end_date, max_scrolls=max_activity_scrolls
            )
        except Exception as e:
            logger.error("Failed to get posts from profile %s: %s", profile_url, e)
            return 0, 0
        logger.info("Found %d post(s) in date range", len(post_urls))
        for j, post_input in enumerate(post_urls, 1):
            logger.info("Syncing post %d/%d: %s", j, len(post_urls), post_input)
            c, u = _sync_leads_for_one_post(
                driver, post_input, persona_id=persona_id, profile_visit_delay_sec=profile_visit_delay_sec
            )
            total_created += c
            total_updated += u
    except RuntimeError:
        raise
    except Exception as e:
        logger.error("Profile sync failed for %r: %s", profile_url, e)
        raise
    finally:
        try:
            driver.quit()
        except Exception as e:
            logger.warning("Driver quit failed: %s", e)
    logger.info("Profile sync complete: created=%d updated=%d", total_created, total_updated)
    return total_created, total_updated


def sync_leads_from_posts(
    post_inputs: list[str],
    *,
    persona_id: int | None = None,
) -> tuple[int, int]:
    total_created, total_updated = 0, 0
    for post_input in post_inputs:
        try:
            c, u = sync_leads_from_post(post_input, persona_id=persona_id)
            total_created += c
            total_updated += u
        except Exception as e:
            logger.error("Sync failed for post %r: %s", post_input, e)
            raise
    return total_created, total_updated
