"""
Normalize LinkedIn post identifiers to activity URN for API calls.
"""

import re
from urllib.parse import urlparse


def activity_urn_from_post_url(url: str) -> str | None:
    """
    Extract activity URN from a post URL or numeric ID.

    Supports:
    - Full URL: .../feed/update/urn:li:activity:7302346926123798528/
    - Full URL: .../posts/...-activity-7302346926123798528-...
    - Numeric ID only: 7302346926123798528
    """
    if not url or not str(url).strip():
        return None
    text = str(url).strip()

    # Already an URN
    if text.startswith("urn:li:activity:"):
        return text

    # Numeric only
    if re.match(r"^\d+$", text):
        return f"urn:li:activity:{text}"

    # URL: feed/update/urn:li:activity:XXXX
    match = re.search(r"urn:li:activity:(\d+)", text, re.I)
    if match:
        return f"urn:li:activity:{match.group(1)}"

    # URL: ...-activity-XXXX-... (posts style)
    match = re.search(r"-activity-(\d+)(?:-|/|$)", text, re.I)
    if match:
        return f"urn:li:activity:{match.group(1)}"

    return None


def activity_id_from_urn(urn: str) -> str | None:
    """Return the numeric activity ID from an activity URN."""
    if not urn or not urn.startswith("urn:li:activity:"):
        return None
    return urn.replace("urn:li:activity:", "", 1)
