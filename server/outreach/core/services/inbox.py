from agent.agent import handle_inbox_reply
from core.exceptions import ExpectedError
from core.models import EmailThread, SentEmail
from core.rate_limit import rate_limit_llm_outreach


class InboxService:
    def build_thread_messages(self, thread: EmailThread) -> list[dict]:
        messages: list[dict] = []
        emails = thread.emails.order_by("sent_at")
        recent = emails[max(0, emails.count() - 10) :]
        for email in recent:
            author = "you" if email.direction == SentEmail.Direction.OUTBOUND else "lead"
            body = (email.body or "")[:2000]
            messages.append({"author": author, "body": body})
        return messages

    def handle_reply(self, payload: dict) -> dict:
        thread_id = (payload.get("thread_id") or "").strip()
        raw_body = (payload.get("raw_body") or "").strip()
        from_email = (payload.get("from_email") or "").strip()
        lead_id = payload.get("lead_id")
        user_id = payload.get("user_id") or 0

        if not raw_body:
            raise ExpectedError("raw_body is required")

        thread = None
        if thread_id:
            thread = EmailThread.objects.filter(gmail_thread_id=thread_id).first()
        if thread is None and lead_id is not None:
            thread = EmailThread.objects.filter(lead_id=lead_id).first()
            if thread and thread_id:
                thread.gmail_thread_id = thread_id
                thread.save(update_fields=["gmail_thread_id"])
        if thread is None:
            raise ExpectedError("thread not found")

        user_id = getattr(thread, "user_id", user_id) or 0

        lead = {
            "email": from_email or "",
            "company_name": thread.company_name or "",
        }

        research = {
            "website_summary": thread.research_summary or "",
            "pain_points": thread.pain_points or [],
            "use_cases": thread.use_cases or [],
        }

        thread_messages = self.build_thread_messages(thread)

        new_message = {"body": raw_body}

        SentEmail.objects.create(
            thread=thread,
            message_id="",
            direction=SentEmail.Direction.INBOUND,
            body=raw_body,
        )

        rate_limit_llm_outreach()
        return handle_inbox_reply(
            thread_messages=thread_messages,
            new_message=new_message,
            lead=lead,
            research=research,
            user_id=user_id,
        )


def handle_inbox_reply_from_http(payload: dict) -> dict:
    return InboxService().handle_reply(payload)
