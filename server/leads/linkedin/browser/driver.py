import os
import re
import subprocess
from typing import Any

from linkedin.core.session import _find_chrome_binary


def _chrome_major_version(chrome_binary: str) -> int | None:
    try:
        out = subprocess.run(
            [chrome_binary, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        text = (out.stdout or "") + (out.stderr or "")
        m = re.search(r"(?:Chromium|Google Chrome)\s+(\d+)", text, re.I)
        if m:
            return int(m.group(1))
        m = re.search(r"\b(\d{2,3})\.\d+\.\d+\.\d+\b", text)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None


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

    major = _chrome_major_version(chrome_binary)
    env_major = (os.environ.get("LINKEDIN_CHROME_VERSION_MAIN") or "").strip()
    if env_major.isdigit():
        major = int(env_major)

    kwargs: dict[str, Any] = {}
    if major is not None:
        kwargs["version_main"] = major

    return uc.Chrome(options=options, **kwargs)
