import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from uuid import uuid4

from core.exceptions import ExpectedError, TransientError


def _raise_smtp_error(exc: Exception) -> None:
    if isinstance(exc, smtplib.SMTPAuthenticationError):
        raise ExpectedError(f"Gmail SMTP auth failed: {exc}") from exc
    if isinstance(exc, smtplib.SMTPDataError):
        raise ExpectedError(f"Gmail SMTP rejected message: {exc}") from exc
    if isinstance(exc, (OSError, ConnectionError, TimeoutError, socket.timeout)):
        raise TransientError(f"Gmail SMTP connection error: {exc}") from exc
    if isinstance(exc, (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected)):
        raise TransientError(f"Gmail SMTP transient error: {exc}") from exc
    raise TransientError(f"Gmail SMTP error: {exc}") from exc


def send_via_smtp(sender: str, password: str, to_email: str, subject: str, body: str) -> tuple[str, str]:
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())
    except Exception as e:
        _raise_smtp_error(e)
    return uuid4().hex, ""
