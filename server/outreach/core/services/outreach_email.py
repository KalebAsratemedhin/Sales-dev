import os
from datetime import datetime, timezone
from uuid import uuid4

from agent.agent import draft_outreach_email
from core.email import send_via_smtp
from core.exceptions import ExpectedError, TransientError
from core.messaging.publish import publish_lead_status_update
from core.models import EmailThread, SentEmail
from core.rate_limit import rate_limit_gmail, rate_limit_llm_outreach


def send_email(to_email: str, subject: str, body: str) -> tuple[str, str]:
    """Send via Gmail SMTP (app password) when configured, else return a stub id."""
    sender = (os.environ.get("GMAIL_SENDER") or "").strip()
    password = (os.environ.get("GMAIL_PASSWORD") or "").strip()

    if sender and password:
        rate_limit_gmail()
        return send_via_smtp(sender, password, to_email, subject, body)
    return f"stub-{uuid4().hex}", f"stub-thread-{uuid4().hex}"


class OutreachEmailService:
    def _has_outbound_email(self, lead_id: int) -> bool:
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
    ) -> EmailThread:
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

    def _send_email(self, to_email: str, subject: str, body: str) -> tuple[str, str]:
        return send_email(to_email, subject, body)

    def run_from_payload(self, payload: dict) -> None:
        lead_id = payload.get("lead_id")
        user_id = payload.get("user_id") or 0
        email = (payload.get("email") or "").strip()

        if lead_id is None:
            raise ExpectedError("missing lead_id")

        if not email:
            raise ExpectedError("missing email")

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

        message_id, thread_id = self._send_email(email, subject, body)

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
            body=body,
        )

        publish_lead_status_update(lead_id, "emailed")


def run_outreach_from_payload(payload: dict) -> None:
    OutreachEmailService().run_from_payload(payload)
