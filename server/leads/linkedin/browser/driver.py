from typing import Any

from linkedin.core.session import _find_chrome_binary


def create_driver(*, headless: bool = True) -> Any:
    try:
        import undetected_chromedriver as uc
    except ImportError as e:
        raise ImportError(
            "linkedin browser requires undetected-chromedriver. "
            "Install with: pip install selenium undetected-chromedriver"
        ) from e
    chrome_binary = _find_chrome_binary()
    if not chrome_binary:
        raise RuntimeError("Chrome/Chromium not found. Install it or set LINKEDIN_CHROME_PATH.")
    options = uc.ChromeOptions()
    options.binary_location = chrome_binary
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return uc.Chrome(options=options)
