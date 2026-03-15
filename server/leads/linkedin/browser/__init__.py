from linkedin.browser.driver import create_driver
from linkedin.browser.engagement import (
    get_engagement_profile_urls_via_browser,
    load_post_and_get_engagement_urls,
    prepare_driver_for_linkedin,
)
from linkedin.browser.posts import get_posts_from_profile_between_dates
from linkedin.browser.profile import (
    DEFAULT_PROFILE_VISIT_DELAY_SEC,
    get_profile_info,
)


def get_engagement_for_post(post_input: str, *, headless: bool = True) -> list[str]:
    return get_engagement_profile_urls_via_browser(post_input, headless=headless)


__all__ = [
    "create_driver",
    "prepare_driver_for_linkedin",
    "load_post_and_get_engagement_urls",
    "get_engagement_profile_urls_via_browser",
    "get_engagement_for_post",
    "get_profile_info",
    "get_posts_from_profile_between_dates",
    "DEFAULT_PROFILE_VISIT_DELAY_SEC",
]
