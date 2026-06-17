import re

_QUOTE_LINE_MARKERS = (
    "-----original message-----",
    "________________________________",
    "---------- forwarded message ---------",
)

_ON_WROTE_RE = re.compile(r"^On .+ wrote:\s*$", re.IGNORECASE)
_FROM_LINE_RE = re.compile(r"^From:\s", re.IGNORECASE)
_SENT_LINE_RE = re.compile(r"^Sent:\s", re.IGNORECASE)
_DATE_LINE_RE = re.compile(r"^Date:\s", re.IGNORECASE)
_SUBJECT_LINE_RE = re.compile(r"^Subject:\s", re.IGNORECASE)
_TO_LINE_RE = re.compile(r"^To:\s", re.IGNORECASE)
_INLINE_ON_WROTE_RE = re.compile(r"\nOn .+ wrote:\s*\n", re.IGNORECASE)


def _strip_html(text: str) -> str:
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p>", "\n", text)
    text = re.sub(r"(?i)</div>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return text


def strip_quoted_reply(text: str) -> str:
    """Return only the new reply text, without quoted prior messages."""
    if not text:
        return ""

    body = _strip_html(text).replace("\r\n", "\n").strip()
    inline = _INLINE_ON_WROTE_RE.search(body)
    if inline:
        body = body[: inline.start()].strip()

    lines = body.split("\n")
    kept: list[str] = []
    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()

        if stripped.startswith(">"):
            break
        if lower in _QUOTE_LINE_MARKERS:
            break
        if _ON_WROTE_RE.match(stripped):
            break
        if _FROM_LINE_RE.match(stripped) and kept and not kept[-1].strip():
            break
        if _SENT_LINE_RE.match(stripped) and kept:
            break
        if _DATE_LINE_RE.match(stripped) and kept and not kept[-1].strip():
            break
        if _SUBJECT_LINE_RE.match(stripped) and kept and not kept[-1].strip():
            break
        if _TO_LINE_RE.match(stripped) and kept and not kept[-1].strip():
            break

        kept.append(line)

    return "\n".join(kept).strip()
