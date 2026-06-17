import os
from uuid import uuid4

from core.email import finalize_email_body
from core.email.gmail_api import send_via_gmail_api
from core.exceptions import ExpectedError
from core.rate_limit import rate_limit_gmail
from core.services.google_oauth import is_connected


def send_email(
    to_email: str,
    subject: str,
    body: str,
    *,
    user_id: int = 0,
    calendly_link: str = "",
    gmail_thread_id: str = "",
) -> tuple[str, str, str]:
    """Send via Gmail API using the user's Google connection. Returns (message_id, thread_id, plain_body)."""
    plain, html = finalize_email_body(body, calendly_link=calendly_link)

    if not user_id:
        raise ExpectedError("user_id is required to send email")

    if not is_connected(user_id):
        raise ExpectedError("Connect Google in Settings to send email (Gmail + Calendar)")

    rate_limit_gmail()
    message_id, thread_id = send_via_gmail_api(
        user_id,
        to_email,
        subject,
        plain,
        html_body=html,
        gmail_thread_id=gmail_thread_id,
    )
    return message_id, thread_id, plain


def send_email_stub(to_email: str, subject: str, body: str, *, calendly_link: str = "") -> tuple[str, str, str]:
    """Dev fallback when SMTP env is set but Google is not connected (legacy)."""
    from core.email.send import send_via_smtp

    plain, html = finalize_email_body(body, calendly_link=calendly_link)
    sender = (os.environ.get("GMAIL_SENDER") or "").strip()
    password = (os.environ.get("GMAIL_PASSWORD") or "").strip()
    if sender and password:
        rate_limit_gmail()
        message_id, thread_id = send_via_smtp(sender, password, to_email, subject, plain, html_body=html)
        return message_id, thread_id, plain
    return f"stub-{uuid4().hex}", f"stub-thread-{uuid4().hex}", plain


class OutreachEmailService:
    def _has_outbound_email(self, lead_id: int) -> bool:
        from core.models import SentEmail

        return SentEmail.objects.filter(
            thread__lead_id=lead_id,
            direction=SentEmail.Direction.OUTBOUND,
        ).exists()

    def _get_or_create_thread(
        self,
        lead_id: int,
        user_id: int,
        to_email: str | None,
        name: str | None,
        subject: str | None,
        gmail_thread_id: str | None,
        company_name: str | None,
        research_summary: str | None,
        pain_points: list,
        use_cases: list,
    ):
        from datetime import datetime, timezone

        from core.models import EmailThread

        thread, _ = EmailThread.objects.get_or_create(lead_id=lead_id, defaults={"user_id": user_id})
        if thread.user_id != user_id:
            thread.user_id = user_id
            thread.save(update_fields=["user_id"])

        thread.to_email = to_email or ""
        thread.name = name or ""
        if subject:
            thread.subject = subject
        if gmail_thread_id:
            thread.gmail_thread_id = gmail_thread_id
        thread.company_name = company_name or ""
        thread.research_summary = research_summary or ""
        thread.pain_points = list(pain_points or [])
        thread.use_cases = list(use_cases or [])
        thread.last_message_at = datetime.now(timezone.utc)
        thread.save()
        return thread

    def run_from_payload(self, payload: dict) -> None:
        from agent.agent import draft_outreach_email
        from core.exceptions import TransientError
        from core.messaging.publish import publish_lead_status_update
        from core.models import SentEmail
        from core.rate_limit import rate_limit_llm_outreach

        lead_id = payload.get("lead_id")
        user_id = payload.get("user_id") or 0
        email = (payload.get("email") or "").strip()

        if lead_id is None:
            raise ExpectedError("missing lead_id")
        if not email:
            raise ExpectedError("missing email")
        if not user_id:
            raise ExpectedError("missing user_id")

        if self._has_outbound_email(lead_id):
            return

        lead = {
            "email": email,
            "name": payload.get("name") or "",
            "company_name": payload.get("company_name") or "",
            "company_website": payload.get("company_website") or "",
        }
        research = {
            "website_summary": payload.get("research_summary") or "",
            "pain_points": payload.get("pain_points") or [],
            "use_cases": payload.get("use_cases") or [],
        }
        persona = payload.get("persona") or {}

        rate_limit_llm_outreach()
        draft = draft_outreach_email(lead, research, persona)
        subject = draft.get("subject") or ""
        body = draft.get("body") or ""
        if not subject or not body:
            raise TransientError("draft_outreach_email returned empty subject/body")

        message_id, thread_id, formatted_body = send_email(email, subject, body, user_id=user_id)

        thread = self._get_or_create_thread(
            lead_id=lead_id,
            user_id=user_id,
            to_email=email,
            name=lead["name"],
            subject=subject,
            gmail_thread_id=thread_id,
            company_name=lead["company_name"],
            research_summary=research["website_summary"],
            pain_points=research["pain_points"],
            use_cases=research["use_cases"],
        )

        SentEmail.objects.create(
            thread=thread,
            message_id=message_id,
            direction=SentEmail.Direction.OUTBOUND,
            body=formatted_body,
        )
        publish_lead_status_update(lead_id, "emailed")


def run_outreach_from_payload(payload: dict) -> None:
    OutreachEmailService().run_from_payload(payload)
