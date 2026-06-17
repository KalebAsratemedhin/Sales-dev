import base64
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.exceptions import ExpectedError, TransientError
from core.services.google_oauth import get_credentials

logger = logging.getLogger("gmail_api")


def send_via_gmail_api(
    user_id: int,
    to_email: str,
    subject: str,
    plain: str,
    *,
    html_body: str | None = None,
    gmail_thread_id: str = "",
) -> tuple[str, str]:
    if not user_id:
        raise ExpectedError("user_id is required to send email via Gmail")

    creds = get_credentials(user_id)
    from googleapiclient.discovery import build

    try:
        service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    except Exception as e:
        raise TransientError(f"Gmail API client error: {e}") from e

    from core.services.google_oauth import resolve_google_email

    from_email = resolve_google_email(user_id, gmail_service=service)

    if not from_email:
        raise ExpectedError("Connected Google account has no email address")

    sender_name = (os.environ.get("GMAIL_SENDER_NAME") or "").strip()
    msg = MIMEMultipart("alternative")
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["From"] = f"{sender_name} <{from_email}>" if sender_name else from_email
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    if html_body:
        msg.attach(MIMEText(html_body, "html", "utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
    body: dict = {"raw": raw}
    if gmail_thread_id:
        body["threadId"] = gmail_thread_id

    try:
        sent = service.users().messages().send(userId="me", body=body).execute()
    except ExpectedError:
        raise
    except Exception as e:
        text = str(e).lower()
        if "invalid_grant" in text or "unauthorized" in text:
            raise ExpectedError(f"Gmail auth failed — reconnect in Settings: {e}") from e
        raise TransientError(f"Gmail API send error: {e}") from e

    return sent.get("id") or "", sent.get("threadId") or ""
