import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from core.exceptions import ExpectedError, TransientError
from core.models import GoogleConnection, OutreachConfig
from core.services.n8n_client import n8n_configured
from core.services.n8n_gmail_sync import sync_gmail_to_n8n, teardown_n8n_gmail

logger = logging.getLogger("google_oauth")

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/userinfo.email",
]
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def oauth_app_configured() -> bool:
    return bool(_client_id() and _client_secret() and _redirect_uri())


def _client_id() -> str:
    return (os.environ.get("GOOGLE_OAUTH_CLIENT_ID") or "").strip()


def _client_secret() -> str:
    return (os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET") or "").strip()


def _redirect_uri() -> str:
    return (
        os.environ.get("GOOGLE_OAUTH_REDIRECT_URI") or "http://localhost:3000/settings/google-callback"
    ).strip()


def _require_oauth_app() -> None:
    if not oauth_app_configured():
        raise ExpectedError(
            "Google OAuth is not configured. Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET."
        )


def _require_n8n() -> None:
    if not n8n_configured():
        raise ExpectedError(
            "n8n API is not configured. Create an API key in n8n (Settings → API) and set N8N_API_KEY."
        )


def get_connection(user_id: int) -> GoogleConnection | None:
    if not user_id:
        return None
    return GoogleConnection.objects.filter(user_id=user_id).first()


def is_connected(user_id: int) -> bool:
    conn = get_connection(user_id)
    return bool(conn and conn.refresh_token)


def connection_status(user_id: int) -> dict:
    conn = get_connection(user_id)
    if not conn or not conn.refresh_token:
        return {
            "connected": False,
            "oauth_app_configured": oauth_app_configured(),
            "n8n_configured": n8n_configured(),
        }

    config = OutreachConfig.get_singleton()
    n8n_synced = bool(conn.n8n_credential_id and conn.n8n_workflow_id and not conn.n8n_sync_error)
    return {
        "connected": True,
        "oauth_app_configured": oauth_app_configured(),
        "google_email": conn.google_email or "",
        "gmail_configured": True,
        "calendar_configured": True,
        "n8n_configured": n8n_configured(),
        "n8n_synced": n8n_synced,
        "n8n_credential_id": conn.n8n_credential_id or "",
        "n8n_workflow_id": conn.n8n_workflow_id or "",
        "n8n_sync_error": conn.n8n_sync_error or "",
        "calendar_id": conn.calendar_id or "primary",
        "timezone": conn.timezone or config.default_timezone or "UTC",
        "meeting_duration_minutes": conn.meeting_duration_minutes or config.default_meeting_duration_minutes or 30,
        "connected_at": conn.connected_at.isoformat() if conn.connected_at else None,
        "n8n_synced_at": conn.n8n_synced_at.isoformat() if conn.n8n_synced_at else None,
    }


def build_authorize_url(user_id: int) -> dict:
    _require_oauth_app()
    _require_n8n()
    state = secrets.token_urlsafe(24)
    GoogleConnection.objects.update_or_create(
        user_id=user_id,
        defaults={"oauth_state": state},
    )
    params = {
        "client_id": _client_id(),
        "redirect_uri": _redirect_uri(),
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return {"url": f"{AUTH_URL}?{urlencode(params)}", "state": state}


def exchange_code(user_id: int, code: str, state: str = "") -> GoogleConnection:
    _require_oauth_app()
    if not code:
        raise ExpectedError("missing authorization code")

    conn = get_connection(user_id)
    if conn and conn.oauth_state and state and conn.oauth_state != state:
        raise ExpectedError("invalid OAuth state")

    try:
        resp = requests.post(
            TOKEN_URL,
            data={
                "code": code,
                "client_id": _client_id(),
                "client_secret": _client_secret(),
                "redirect_uri": _redirect_uri(),
                "grant_type": "authorization_code",
            },
            timeout=20,
        )
    except requests.RequestException as e:
        raise TransientError(f"Google token exchange failed: {e}") from e

    if resp.status_code >= 400:
        raise ExpectedError(f"Google token exchange failed: {resp.text[:300]}")

    data = resp.json()
    refresh_token = (data.get("refresh_token") or "").strip()
    access_token = (data.get("access_token") or "").strip()
    if not refresh_token and conn:
        refresh_token = conn.refresh_token
    if not refresh_token:
        raise ExpectedError("Google did not return a refresh token. Revoke app access and reconnect.")

    expires_in = int(data.get("expires_in") or 0)
    expires_at = None
    if expires_in:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

    google_email = ""
    if access_token:
        try:
            info = requests.get(
                USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=15,
            )
            if info.status_code < 400:
                google_email = (info.json().get("email") or "").strip()
        except requests.RequestException:
            logger.warning("Could not fetch Google userinfo for user_id=%s", user_id)

    conn, _ = GoogleConnection.objects.update_or_create(
        user_id=user_id,
        defaults={
            "refresh_token": refresh_token,
            "access_token": access_token,
            "expires_at": expires_at,
            "scope": (data.get("scope") or " ".join(SCOPES)).strip(),
            "google_email": google_email,
            "oauth_state": "",
        },
    )

    if not conn.google_email:
        resolve_google_email(user_id)

    sync_gmail_to_n8n(conn)
    if conn.n8n_sync_error:
        raise ExpectedError(conn.n8n_sync_error)

    return conn


def disconnect(user_id: int) -> None:
    conn = get_connection(user_id)
    if conn:
        teardown_n8n_gmail(conn)
        conn.delete()


def resync_n8n(user_id: int) -> dict:
    conn = get_connection(user_id)
    if not conn or not conn.refresh_token:
        raise ExpectedError("Google is not connected")
    sync_gmail_to_n8n(conn)
    return connection_status(user_id)


def update_settings(
    user_id: int,
    *,
    calendar_id: str | None = None,
    timezone: str | None = None,
    duration: int | None = None,
) -> dict:
    conn = get_connection(user_id)
    if not conn or not conn.refresh_token:
        raise ExpectedError("Google is not connected")

    fields = []
    if calendar_id is not None:
        conn.calendar_id = calendar_id.strip() or "primary"
        fields.append("calendar_id")
    if timezone is not None:
        conn.timezone = timezone.strip()
        fields.append("timezone")
    if duration is not None:
        conn.meeting_duration_minutes = max(15, min(int(duration), 180))
        fields.append("meeting_duration_minutes")
    if fields:
        fields.append("updated_at")
        conn.save(update_fields=fields)
    return connection_status(user_id)


def _connection(user_id: int) -> GoogleConnection:
    conn = get_connection(user_id)
    if not conn or not conn.refresh_token:
        raise ExpectedError("Google is not connected for this user")
    return conn


def resolve_google_email(user_id: int, *, gmail_service=None) -> str:
    """Return connected account email, fetching from Gmail profile if not stored."""
    conn = get_connection(user_id)
    if not conn:
        return ""
    if conn.google_email:
        return conn.google_email

    creds = get_credentials(user_id)
    email = ""

    if gmail_service is None:
        try:
            from googleapiclient.discovery import build

            gmail_service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        except Exception as e:
            logger.warning("Gmail client build failed for user_id=%s: %s", user_id, e)
            gmail_service = None

    if gmail_service is not None:
        try:
            profile = gmail_service.users().getProfile(userId="me").execute()
            email = (profile.get("emailAddress") or "").strip()
        except Exception as e:
            logger.warning("Gmail profile fetch failed for user_id=%s: %s", user_id, e)

    if not email and creds.token:
        try:
            info = requests.get(
                USERINFO_URL,
                headers={"Authorization": f"Bearer {creds.token}"},
                timeout=15,
            )
            if info.status_code < 400:
                email = (info.json().get("email") or "").strip()
        except requests.RequestException as e:
            logger.warning("Userinfo fetch failed for user_id=%s: %s", user_id, e)

    if email:
        conn.google_email = email
        conn.save(update_fields=["google_email", "updated_at"])

    return email


def _granted_scopes(conn: GoogleConnection) -> list[str]:
    scopes = [s.strip() for s in (conn.scope or "").split() if s.strip()]
    return scopes or list(SCOPES)


def get_credentials(user_id: int) -> Credentials:
    conn = _connection(user_id)
    creds = Credentials(
        token=conn.access_token or None,
        refresh_token=conn.refresh_token,
        token_uri=TOKEN_URL,
        client_id=_client_id(),
        client_secret=_client_secret(),
        scopes=_granted_scopes(conn),
    )
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            text = str(e).lower()
            if "invalid_grant" in text or "unauthorized" in text:
                raise ExpectedError("Google auth expired — reconnect in Settings") from e
            raise TransientError(f"Google token refresh failed: {e}") from e
        conn.access_token = creds.token or ""
        if creds.expiry:
            conn.expires_at = creds.expiry.replace(tzinfo=timezone.utc)
        conn.save(update_fields=["access_token", "expires_at", "updated_at"])
    return creds
