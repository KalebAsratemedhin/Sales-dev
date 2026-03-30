"""Scrape one LinkedIn profile URL and create or update a Lead."""

import logging
import time

from linkedin.browser import get_profile_info

from .lead_records import (
    build_name,
    get_or_create_linkedin_lead,
    persist_existing_lead_updates,
)

logger = logging.getLogger(__name__)


def fetch_profile_info(driver, profile_url: str) -> dict | None:
    try:
        return get_profile_info(driver, profile_url)
    except Exception as e:
        logger.warning("Failed to scrape profile %s: %s", profile_url, e)
        return None


def process_one_profile_url(
    driver,
    profile_url: str,
    *,
    index: int,
    total: int,
    comment_url_set: frozenset[str],
    persona_id: int | None,
    user_id: int | None,
    profile_visit_delay_sec: float,
) -> tuple[int, int]:
    """Returns (created_delta, updated_delta)."""
    logger.info("Processing profile %d/%d: %s", index, total, profile_url)
    info = fetch_profile_info(driver, profile_url)
    if info is None:
        return 0, 0

    name = build_name(info)
    scraped_email = (info.get("email") or "").strip()
    scraped_website = (info.get("website") or "").strip()
    logger.info(
        "Scraped: name=%r email=%s website=%s",
        name or "(none)",
        scraped_email or "(placeholder)",
        scraped_website or "(none)",
    )

    pair = get_or_create_linkedin_lead(
        profile_url, user_id, persona_id, name, scraped_email, scraped_website
    )
    if pair is None:
        return 0, 0

    lead, was_created = pair
    if was_created:
        logger.info("Lead created: id=%s profile_url=%s", lead.id, profile_url)
        time.sleep(profile_visit_delay_sec)
        return 1, 0

    if not persist_existing_lead_updates(
        lead,
        profile_url,
        name=name,
        scraped_email=scraped_email,
        scraped_website=scraped_website,
        comment_url_set=comment_url_set,
    ):
        return 0, 0

    logger.info("Lead updated: id=%s profile_url=%s", lead.id, profile_url)
    time.sleep(profile_visit_delay_sec)
    return 0, 1
