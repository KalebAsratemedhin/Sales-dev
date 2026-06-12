import logging
import os
from datetime import datetime, timedelta, timezone

from core.exceptions import ExpectedError, TransientError

logger = logging.getLogger("google_calendar")

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def calendar_configured() -> bool:
    return bool(
        (os.environ.get("GOOGLE_OAUTH_CLIENT_ID") or "").strip()
        and (os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET") or "").strip()
        and (os.environ.get("GOOGLE_CALENDAR_REFRESH_TOKEN") or "").strip()
    )


def _credentials():
    from google.oauth2.credentials import Credentials

    client_id = (os.environ.get("GOOGLE_OAUTH_CLIENT_ID") or "").strip()
    client_secret = (os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET") or "").strip()
    refresh_token = (os.environ.get("GOOGLE_CALENDAR_REFRESH_TOKEN") or "").strip()

    if not all([client_id, client_secret, refresh_token]):
        raise ExpectedError(
            "Google Calendar not configured. Set GOOGLE_OAUTH_CLIENT_ID, "
            "GOOGLE_OAUTH_CLIENT_SECRET, and GOOGLE_CALENDAR_REFRESH_TOKEN."
        )

    return Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )


def _calendar_service():
    from googleapiclient.discovery import build

    return build("calendar", "v3", credentials=_credentials(), cache_discovery=False)


def _calendar_id() -> str:
    return (os.environ.get("GOOGLE_CALENDAR_ID") or os.environ.get("GMAIL_SENDER") or "primary").strip()


def _default_tz() -> str:
    return (os.environ.get("DEFAULT_TIMEZONE") or "UTC").strip()


def _parse_start(start_iso: str) -> datetime:
    raw = (start_iso or "").strip()
    if not raw:
        raise ExpectedError("missing meeting start time")

    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(raw)
    except ValueError as e:
        raise ExpectedError(f"invalid meeting start time: {start_iso}") from e

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def create_meeting_event(
    *,
    title: str,
    start_iso: str,
    duration_minutes: int,
    lead_email: str,
    lead_name: str = "",
    company_name: str = "",
    description: str = "",
) -> dict:
    if not calendar_configured():
        raise ExpectedError("Google Calendar is not configured")

    start = _parse_start(start_iso)
    duration = max(15, min(int(duration_minutes or 30), 180))
    end = start + timedelta(minutes=duration)
    tz = _default_tz()

    owner_email = (os.environ.get("GMAIL_SENDER") or "").strip()
    attendees = []
    if owner_email:
        attendees.append({"email": owner_email, "responseStatus": "accepted"})
    if lead_email:
        attendees.append({"email": lead_email})

    body = {
        "summary": title or "Sales call",
        "description": description or f"Intro call with {lead_name or lead_email} ({company_name or 'prospect'}).",
        "start": {"dateTime": start.isoformat(), "timeZone": tz},
        "end": {"dateTime": end.isoformat(), "timeZone": tz},
        "attendees": attendees,
        "reminders": {"useDefault": True},
    }

    try:
        service = _calendar_service()
        created = (
            service.events()
            .insert(
                calendarId=_calendar_id(),
                body=body,
                sendUpdates="all",
            )
            .execute()
        )
    except ExpectedError:
        raise
    except Exception as e:
        text = str(e).lower()
        if "invalid_grant" in text or "unauthorized" in text:
            raise ExpectedError(f"Google Calendar auth failed: {e}") from e
        raise TransientError(f"Google Calendar API error: {e}") from e

    return {
        "event_id": created.get("id") or "",
        "html_link": created.get("htmlLink") or "",
        "start_iso": start.isoformat(),
        "end_iso": end.isoformat(),
        "timezone": tz,
    }
