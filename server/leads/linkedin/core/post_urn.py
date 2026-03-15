import re


def activity_urn_from_post_url(url: str) -> str | None:
    if not url or not str(url).strip():
        return None
    text = str(url).strip()
    if text.startswith("urn:li:activity:"):
        return text
    if re.match(r"^\d+$", text):
        return f"urn:li:activity:{text}"
    match = re.search(r"urn:li:activity:(\d+)", text, re.I)
    if match:
        return f"urn:li:activity:{match.group(1)}"
    match = re.search(r"-activity-(\d+)(?:-|/|$)", text, re.I)
    if match:
        return f"urn:li:activity:{match.group(1)}"
    return None


def activity_id_from_urn(urn: str) -> str | None:
    if not urn or not urn.startswith("urn:li:activity:"):
        return None
    return urn.replace("urn:li:activity:", "", 1)
