import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import requests

from core.exceptions import ExpectedError, TransientError
from core.models import GmailConnection
from core.services.n8n_client import n8n_configured
from core.services.n8n_gmail_sync import sync_gmail_to_n8n, teardown_n8n_gmail

logger = logging.getLogger("google_gmail_oauth")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
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
        os.environ.get("GOOGLE_OAUTH_GMAIL_REDIRECT_URI")
        or "http://localhost:3000/settings/gmail-callback"
    ).strip()


def _require_oauth_app() -> None:
    if not oauth_app_configured():
        raise ExpectedError(
            "Gmail OAuth is not configured. Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET."
        )


def get_connection(user_id: int) -> GmailConnection | None:
    if not user_id:
        return None
    return GmailConnection.objects.filter(user_id=user_id).first()


def connection_status(user_id: int) -> dict:
    conn = get_connection(user_id)
    if not conn or not conn.refresh_token:
        return {
            "connected": False,
            "oauth_app_configured": oauth_app_configured(),
            "n8n_configured": n8n_configured(),
        }

    n8n_synced = bool(conn.n8n_credential_id and conn.n8n_workflow_id and not conn.n8n_sync_error)
    return {
        "connected": True,
        "oauth_app_configured": oauth_app_configured(),
        "google_email": conn.google_email or "",
        "n8n_configured": n8n_configured(),
        "n8n_synced": n8n_synced,
        "n8n_credential_id": conn.n8n_credential_id or "",
        "n8n_workflow_id": conn.n8n_workflow_id or "",
        "n8n_sync_error": conn.n8n_sync_error or "",
        "connected_at": conn.connected_at.isoformat() if conn.connected_at else None,
        "n8n_synced_at": conn.n8n_synced_at.isoformat() if conn.n8n_synced_at else None,
    }


def _require_n8n() -> None:
    if not n8n_configured():
        raise ExpectedError(
            "n8n API is not configured. Create an API key in n8n (Settings → API) and set N8N_API_KEY in server/.env."
        )


def build_authorize_url(user_id: int) -> dict:
    _require_oauth_app()
    _require_n8n()
    state = secrets.token_urlsafe(24)
    GmailConnection.objects.update_or_create(
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


def exchange_code(user_id: int, code: str, state: str = "") -> GmailConnection:
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

    conn, _ = GmailConnection.objects.update_or_create(
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
        raise ExpectedError("Gmail is not connected")
    sync_gmail_to_n8n(conn)
    return connection_status(user_id)
