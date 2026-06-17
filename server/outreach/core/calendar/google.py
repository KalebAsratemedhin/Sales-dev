import logging
from datetime import datetime, timedelta, timezone

from core.exceptions import ExpectedError, TransientError
from core.models import GoogleConnection, OutreachConfig
from core.services.google_oauth import SCOPES, get_credentials, is_connected, oauth_app_configured

logger = logging.getLogger("google_calendar")


def calendar_configured(user_id: int) -> bool:
    return oauth_app_configured() and is_connected(user_id)


def _connection(user_id: int) -> GoogleConnection:
    conn = GoogleConnection.objects.filter(user_id=user_id).first()
    if not conn or not conn.refresh_token:
        raise ExpectedError("Google is not connected for this user")
    return conn


def _calendar_service(user_id: int):
    from googleapiclient.discovery import build

    return build("calendar", "v3", credentials=get_credentials(user_id), cache_discovery=False)


def _calendar_id(user_id: int) -> str:
    conn = _connection(user_id)
    return (conn.calendar_id or "primary").strip()


def _default_tz(user_id: int) -> str:
    conn = _connection(user_id)
    if conn.timezone:
        return conn.timezone.strip()
    config = OutreachConfig.get_singleton()
    return (config.default_timezone or "UTC").strip()


def _default_duration(user_id: int) -> int:
    conn = _connection(user_id)
    if conn.meeting_duration_minutes:
        return conn.meeting_duration_minutes
    config = OutreachConfig.get_singleton()
    return config.default_meeting_duration_minutes or 30


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
    user_id: int,
    title: str,
    start_iso: str,
    duration_minutes: int | None = None,
    lead_email: str,
    lead_name: str = "",
    company_name: str = "",
    description: str = "",
) -> dict:
    if not calendar_configured(user_id):
        raise ExpectedError("Google is not connected for this user")

    start = _parse_start(start_iso)
    duration = max(15, min(int(duration_minutes or _default_duration(user_id)), 180))
    end = start + timedelta(minutes=duration)
    tz = _default_tz(user_id)
    conn = _connection(user_id)

    attendees = []
    if conn.google_email:
        attendees.append({"email": conn.google_email, "responseStatus": "accepted"})
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
        service = _calendar_service(user_id)
        created = (
            service.events()
            .insert(
                calendarId=_calendar_id(user_id),
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
            raise ExpectedError(f"Google Calendar auth failed — reconnect in Settings: {e}") from e
        raise TransientError(f"Google Calendar API error: {e}") from e

    return {
        "event_id": created.get("id") or "",
        "html_link": created.get("htmlLink") or "",
        "start_iso": start.isoformat(),
        "end_iso": end.isoformat(),
        "timezone": tz,
    }
