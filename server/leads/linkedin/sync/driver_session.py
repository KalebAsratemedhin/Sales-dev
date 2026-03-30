"""Selenium driver lifecycle for LinkedIn sync."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from linkedin.browser import create_driver, prepare_driver_for_linkedin
from linkedin.core.constants import SESSION_REQUIRED_MSG

logger = logging.getLogger(__name__)


@contextmanager
def linkedin_driver(headless: bool) -> Iterator[Any]:
    driver = create_driver(headless=headless)
    logger.info("Browser driver created (headless=%s)", headless)
    try:
        yield driver
    finally:
        try:
            driver.quit()
        except Exception as e:
            logger.warning("Driver quit failed: %s", e)


def require_session_and_prepare(driver) -> None:
    if not prepare_driver_for_linkedin(driver):
        raise RuntimeError(SESSION_REQUIRED_MSG)
