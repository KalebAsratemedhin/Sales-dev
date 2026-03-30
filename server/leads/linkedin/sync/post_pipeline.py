"""Load post engagement and sync leads for one or many posts from a profile."""

import logging
from datetime import date

from config.models import LinkedInSyncedPost
from linkedin.browser import (
    DEFAULT_PROFILE_VISIT_DELAY_SEC,
    get_posts_from_profile_between_dates,
    load_post_and_get_engagement_urls,
)
from linkedin.browser.engagement import PostEngagementScrape

from .profile_processing import process_one_profile_url

logger = logging.getLogger(__name__)


def load_post_engagement(driver, post_input: str) -> PostEngagementScrape | None:
    try:
        return load_post_and_get_engagement_urls(driver, post_input)
    except Exception as e:
        logger.error("Failed to load engagement for post %r: %s", post_input, e)
        return None


def record_synced_post(scrape: PostEngagementScrape, user_id: int | None) -> None:
    if not scrape.post_url:
        return
    LinkedInSyncedPost.objects.update_or_create(
        post_url=scrape.post_url,
        defaults={"synced_by_user_id": user_id},
    )


def sync_leads_for_one_post(
    driver,
    post_input: str,
    *,
    persona_id: int | None = None,
    user_id: int | None = None,
    profile_visit_delay_sec: float = DEFAULT_PROFILE_VISIT_DELAY_SEC,
) -> tuple[int, int]:
    logger.info("Loading post and scraping engagement: %r", post_input)
    scrape = load_post_engagement(driver, post_input)
    if scrape is None:
        return 0, 0

    profile_urls = scrape.all_profile_urls
    comment_url_set = frozenset(scrape.comment_profile_urls)
    record_synced_post(scrape, user_id)

    if not profile_urls:
        logger.info("No profile URLs from engagement for %r", post_input)
        return 0, 0

    logger.info("Obtained %d profile URL(s) from engagement", len(profile_urls))
    created, updated = 0, 0
    total = len(profile_urls)
    for i, profile_url in enumerate(profile_urls, 1):
        if not profile_url:
            continue
        c, u = process_one_profile_url(
            driver,
            profile_url,
            index=i,
            total=total,
            comment_url_set=comment_url_set,
            persona_id=persona_id,
            user_id=user_id,
            profile_visit_delay_sec=profile_visit_delay_sec,
        )
        created += c
        updated += u
    return created, updated


def collect_post_urls_from_profile(
    driver,
    profile_url: str,
    start_date: date,
    end_date: date,
    max_activity_scrolls: int,
) -> list[str]:
    try:
        return get_posts_from_profile_between_dates(
            driver, profile_url, start_date, end_date, max_scrolls=max_activity_scrolls
        )
    except Exception as e:
        logger.error("Failed to get posts from profile %s: %s", profile_url, e)
        return []
