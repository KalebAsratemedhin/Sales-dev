from datetime import timedelta

from django.db.models import Count, Max, Q
from django.utils import timezone

from agent.agent import draft_followup_email
from core.exceptions import ExpectedError, TransientError
from core.messaging.publish import publish_lead_status_update
from core.models import EmailThread, SentEmail
from core.rate_limit import rate_limit_llm_outreach
from core.services.outreach_email import send_email


def find_due_thread_ids(days: int) -> list[int]:
    """Thread ids with exactly one outbound email, no inbound reply, where that
    outbound was sent more than `days` ago — i.e. due for a single follow-up."""
    cutoff = timezone.now() - timedelta(days=days)
    qs = (
        EmailThread.objects.annotate(
            outbound=Count("emails", filter=Q(emails__direction=SentEmail.Direction.OUTBOUND)),
            inbound=Count("emails", filter=Q(emails__direction=SentEmail.Direction.INBOUND)),
            last_outbound_at=Max(
                "emails__sent_at", filter=Q(emails__direction=SentEmail.Direction.OUTBOUND)
            ),
        )
        .filter(outbound=1, inbound=0, last_outbound_at__lt=cutoff)
        .exclude(to_email="")
        .values_list("id", flat=True)
    )
    return list(qs)


def _thread_messages(thread: EmailThread) -> list[dict]:
    emails = thread.emails.order_by("sent_at")
    recent = emails[max(0, emails.count() - 10):]
    messages = []
    for email in recent:
        author = "you" if email.direction == SentEmail.Direction.OUTBOUND else "lead"
        messages.append({"author": author, "body": (email.body or "")[:2000]})
    return messages


def send_followup_for_thread(thread_id: int) -> None:
    thread = EmailThread.objects.filter(pk=thread_id).first()
    if thread is None:
        raise ExpectedError("thread not found")

    # Re-check eligibility at send time (state may have changed since dispatch).
    outbound = thread.emails.filter(direction=SentEmail.Direction.OUTBOUND).count()
    inbound = thread.emails.filter(direction=SentEmail.Direction.INBOUND).count()
    if inbound > 0 or outbound != 1:
        return

    to_email = (thread.to_email or "").strip()
    if not to_email:
        raise ExpectedError("thread has no to_email")

    lead = {
        "name": thread.name or "",
        "email": to_email,
        "company_name": thread.company_name or "",
    }
    research = {
        "website_summary": thread.research_summary or "",
        "pain_points": thread.pain_points or [],
        "use_cases": thread.use_cases or [],
    }

    rate_limit_llm_outreach()
    draft = draft_followup_email(lead, research, _thread_messages(thread))

    subject = (draft.get("subject") or "").strip() or (
        f"Re: {thread.subject}" if thread.subject else "Following up"
    )
    body = (draft.get("body") or "").strip()
    if not body:
        raise TransientError("draft_followup_email returned empty body")

    message_id, _ = send_email(to_email, subject, body)

    SentEmail.objects.create(
        thread=thread,
        message_id=message_id,
        direction=SentEmail.Direction.OUTBOUND,
        body=body,
    )
    thread.last_message_at = timezone.now()
    thread.save(update_fields=["last_message_at"])

    publish_lead_status_update(thread.lead_id, "follow_up_required")
