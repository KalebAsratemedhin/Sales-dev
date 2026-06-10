"""Classify Gemini / Google GenAI errors for retry policy."""

PERMANENT = "permanent"
TRANSIENT = "transient"


def _error_text(exc: BaseException) -> str:
    parts = [str(exc)]
    for attr in ("message", "details"):
        val = getattr(exc, attr, None)
        if val and str(val) not in parts:
            parts.append(str(val))
    return " ".join(parts).lower()


def classify_llm_error(exc: BaseException) -> tuple[str, str]:
    """
    Return (kind, message).
    permanent — do not retry (quota exhausted, auth, bad request).
    transient — retry with backoff (network blip, 5xx, short-lived rate limit).
    """
    text = _error_text(exc)
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)

    if code in (401, 403) or "api key" in text or "permission" in text:
        return PERMANENT, f"Gemini auth error: {exc}"

    if code == 400 or "invalid argument" in text:
        return PERMANENT, f"Gemini bad request: {exc}"

    quota_markers = (
        "resource_exhausted",
        "quota exceeded",
        "exceeded your current quota",
        "free_tier",
        "generatecontent_free_tier",
        "perdayperproject",
    )
    if any(m in text for m in quota_markers):
        return PERMANENT, f"Gemini quota exhausted: {exc}"

    if code in (500, 502, 503, 504):
        return TRANSIENT, f"Gemini server error: {exc}"

    transient_markers = ("timeout", "timed out", "connection", "temporarily unavailable")
    if any(m in text for m in transient_markers):
        return TRANSIENT, f"Gemini transient error: {exc}"

    # Unknown — treat as transient once; caller may still cap retries.
    return TRANSIENT, f"Gemini error: {exc}"
