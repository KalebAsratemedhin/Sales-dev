"""Public entrypoints for LinkedIn → Lead sync."""

import logging
from datetime import date

from linkedin.browser import DEFAULT_PROFILE_VISIT_DELAY_SEC
from linkedin.core.constants import SESSION_REQUIRED_MSG
from linkedin.core.session import load_cookies

from .driver_session import linkedin_driver, require_session_and_prepare
from .post_pipeline import (
    collect_post_urls_from_profile,
    sync_leads_for_one_post,
)

logger = logging.getLogger(__name__)


def sync_leads_from_post(
    post_input: str,
    *,
    persona_id: int | None = None,
    user_id: int | None = None,
    headless: bool = True,
    profile_visit_delay_sec: float = DEFAULT_PROFILE_VISIT_DELAY_SEC,
) -> tuple[int, int]:
    logger.info("Starting sync for post_input=%r", post_input)
    if not load_cookies():
        raise RuntimeError(SESSION_REQUIRED_MSG)

    created, updated = 0, 0
    with linkedin_driver(headless) as driver:
        require_session_and_prepare(driver)
        try:
            created, updated = sync_leads_for_one_post(
                driver,
                post_input,
                persona_id=persona_id,
                user_id=user_id,
                profile_visit_delay_sec=profile_visit_delay_sec,
            )
        except RuntimeError:
            raise
        except Exception as e:
            logger.error("Sync failed for post %r: %s", post_input, e)
            raise

    logger.info("Sync complete: created=%d updated=%d", created, updated)
    return created, updated


def sync_leads_from_profile(
    profile_url: str,
    start_date: date,
    end_date: date,
    *,
    persona_id: int | None = None,
    user_id: int | None = None,
    headless: bool = True,
    profile_visit_delay_sec: float = DEFAULT_PROFILE_VISIT_DELAY_SEC,
    max_activity_scrolls: int = 10,
) -> tuple[int, int]:
    logger.info("Starting profile sync: %r between %s and %s", profile_url, start_date, end_date)
    if not load_cookies():
        raise RuntimeError(SESSION_REQUIRED_MSG)

    total_created, total_updated = 0, 0
    with linkedin_driver(headless) as driver:
        require_session_and_prepare(driver)
        try:
            post_urls = collect_post_urls_from_profile(
                driver, profile_url, start_date, end_date, max_activity_scrolls
            )
            logger.info("Found %d post(s) in date range", len(post_urls))
            for j, single_post in enumerate(post_urls, 1):
                logger.info("Syncing post %d/%d: %s", j, len(post_urls), single_post)
                c, u = sync_leads_for_one_post(
                    driver,
                    single_post,
                    persona_id=persona_id,
                    user_id=user_id,
                    profile_visit_delay_sec=profile_visit_delay_sec,
                )
                total_created += c
                total_updated += u
        except RuntimeError:
            raise
        except Exception as e:
            logger.error("Profile sync failed for %r: %s", profile_url, e)
            raise

    logger.info("Profile sync complete: created=%d updated=%d", total_created, total_updated)
    return total_created, total_updated


def sync_leads_from_posts(
    post_inputs: list[str],
    *,
    persona_id: int | None = None,
    user_id: int | None = None,
) -> tuple[int, int]:
    total_created, total_updated = 0, 0
    for post_input in post_inputs:
        try:
            c, u = sync_leads_from_post(post_input, persona_id=persona_id, user_id=user_id)
            total_created += c
            total_updated += u
        except Exception as e:
            logger.error("Sync failed for post %r: %s", post_input, e)
            raise
    return total_created, total_updated
