from django.utils import timezone

from agent.agent import handle_inbox_reply
from core.email import finalize_email_body
from core.email.reply_body import strip_quoted_reply
from core.messaging.publish import publish_lead_status_update
from core.models import EmailThread, SentEmail
from core.rate_limit import rate_limit_llm_outreach
from core.services.scheduling import SchedulingService

_SCHEDULING_MARKERS = (
    "meet",
    "meeting",
    "call",
    "schedule",
    "calendar",
    "available",
    "availability",
    "time works",
    "book a",
    "zoom",
    "teams",
    "google meet",
    "chat tomorrow",
    "chat next",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
)


def _might_want_scheduling(text: str) -> bool:
    t = (text or "").lower()
    return any(marker in t for marker in _SCHEDULING_MARKERS)


class InboxService:
    def _find_thread(self, *, thread_id: str, from_email: str, lead_id) -> EmailThread | None:
        if thread_id:
            thread = EmailThread.objects.filter(gmail_thread_id=thread_id).first()
            if thread:
                return thread

        if lead_id is not None:
            thread = EmailThread.objects.filter(lead_id=lead_id).first()
            if thread:
                return thread

        if from_email:
            thread = (
                EmailThread.objects.filter(to_email__iexact=from_email)
                .order_by("-last_message_at", "-created_at")
                .first()
            )
            if thread:
                return thread

        return None

    def build_thread_messages(self, thread: EmailThread) -> list[dict]:
        messages: list[dict] = []
        emails = thread.emails.order_by("sent_at")
        recent = emails[max(0, emails.count() - 10) :]
        for email in recent:
            author = "you" if email.direction == SentEmail.Direction.OUTBOUND else "lead"
            body = (email.body or "")[:2000]
            messages.append({"author": author, "body": body})
        return messages

    def draft_reply_for_thread(self, thread: EmailThread) -> dict:
        last_inbound = (
            thread.emails.filter(direction=SentEmail.Direction.INBOUND).order_by("-sent_at").first()
        )
        if last_inbound is None:
            raise ExpectedError("no inbound message to reply to")

        lead = {
            "email": thread.to_email or "",
            "company_name": thread.company_name or "",
        }
        research = {
            "website_summary": thread.research_summary or "",
            "pain_points": thread.pain_points or [],
            "use_cases": thread.use_cases or [],
        }
        thread_messages = self.build_thread_messages(thread)
        rate_limit_llm_outreach()
        result = handle_inbox_reply(
            thread_messages=thread_messages,
            new_message={"body": last_inbound.body or ""},
            lead=lead,
            research=research,
            user_id=thread.user_id or 0,
        )
        plain, _ = finalize_email_body(
            result.get("reply_body") or "",
            calendly_link=result.get("calendly_link") or "",
        )
        return {"body": plain}

    def handle_reply(self, payload: dict) -> dict:
        thread_id = (payload.get("thread_id") or "").strip()
        raw_body = (payload.get("raw_body") or "").strip()
        from_email = (payload.get("from_email") or "").strip()
        lead_id = payload.get("lead_id")
        user_id = payload.get("user_id") or 0

        if not raw_body:
            raise ExpectedError("raw_body is required")

        body = strip_quoted_reply(raw_body)
        if not body:
            body = raw_body.strip()

        thread = self._find_thread(thread_id=thread_id, from_email=from_email, lead_id=lead_id)
        if thread is None:
            raise ExpectedError("thread not found")

        if thread_id and not thread.gmail_thread_id:
            thread.gmail_thread_id = thread_id
            thread.save(update_fields=["gmail_thread_id"])

        user_id = getattr(thread, "user_id", user_id) or 0

        lead = {
            "email": from_email or thread.to_email or "",
            "name": thread.name or "",
            "company_name": thread.company_name or "",
        }

        research = {
            "website_summary": thread.research_summary or "",
            "pain_points": thread.pain_points or [],
            "use_cases": thread.use_cases or [],
        }

        thread_messages = self.build_thread_messages(thread)

        new_message = {"body": body}

        SentEmail.objects.create(
            thread=thread,
            message_id="",
            direction=SentEmail.Direction.INBOUND,
            body=body,
        )
        thread.last_message_at = timezone.now()
        thread.save(update_fields=["last_message_at", "gmail_thread_id"])

        if thread.lead_id:
            publish_lead_status_update(thread.lead_id, "replied")

        sched_result = None
        if _might_want_scheduling(body):
            sched_result = SchedulingService().process_inbound(
                thread=thread,
                thread_messages=thread_messages,
                latest_message=body,
                lead=lead,
            )
        if sched_result:
            plain, _ = finalize_email_body(
                sched_result.get("reply_body") or "",
                calendly_link=sched_result.get("calendly_link") or "",
            )
            response = {
                "reply_body": plain,
                "calendly_link": sched_result.get("calendly_link") or "",
                "event_created": sched_result.get("event_created", False),
            }
            if sched_result.get("meeting"):
                response["meeting"] = sched_result["meeting"]
            return response

        rate_limit_llm_outreach()
        result = handle_inbox_reply(
            thread_messages=thread_messages,
            new_message=new_message,
            lead=lead,
            research=research,
            user_id=user_id,
        )
        plain, _ = finalize_email_body(
            result.get("reply_body") or "",
            calendly_link=result.get("calendly_link") or "",
        )
        return {"reply_body": plain, "calendly_link": result.get("calendly_link") or "", "event_created": False}


def handle_inbox_reply_from_http(payload: dict) -> dict:
    return InboxService().handle_reply(payload)
