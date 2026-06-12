import logging
from datetime import datetime, timezone

from agent.scheduling import run_scheduling_agent
from agent.tools import get_calendly_link
from core.calendar import calendar_configured, create_meeting_event
from core.exceptions import ExpectedError
from core.messaging.publish import publish_lead_status_update
from core.models import EmailThread, ScheduledMeeting, SentEmail
from core.rate_limit import rate_limit_llm_outreach

logger = logging.getLogger("scheduling_service")


def _parse_start_dt(start_iso: str) -> datetime:
    raw = (start_iso or "").strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


class SchedulingService:
    def process_inbound(
        self,
        *,
        thread: EmailThread,
        thread_messages: list[dict],
        latest_message: str,
        lead: dict,
    ) -> dict | None:
        """Run scheduling agent. Returns result dict if scheduling-relevant, else None."""
        rate_limit_llm_outreach()
        decision = run_scheduling_agent(
            thread_messages=thread_messages,
            latest_message=latest_message,
            lead={
                "name": lead.get("name") or thread.name or "",
                "email": lead.get("email") or thread.to_email or "",
                "company_name": lead.get("company_name") or thread.company_name or "",
            },
            calendly_link=get_calendly_link(thread.user_id or 0),
        )

        if not decision.scheduling_relevant:
            return None

        result = {
            "scheduling_relevant": True,
            "ready_to_book": decision.ready_to_book,
            "reply_body": decision.reply_body,
            "event_created": False,
            "meeting": None,
            "calendly_link": get_calendly_link(thread.user_id or 0),
        }

        if not decision.ready_to_book or not decision.start_iso.strip():
            return result

        if not calendar_configured():
            logger.warning("Lead ready to book but Google Calendar is not configured")
            return result

        try:
            event = create_meeting_event(
                title=decision.meeting_title
                or f"Call with {lead.get('name') or thread.name or thread.to_email}",
                start_iso=decision.start_iso,
                duration_minutes=decision.duration_minutes,
                lead_email=lead.get("email") or thread.to_email or "",
                lead_name=lead.get("name") or thread.name or "",
                company_name=lead.get("company_name") or thread.company_name or "",
            )
        except ExpectedError:
            raise
        except Exception:
            logger.exception("Failed to create calendar event for thread %s", thread.id)
            return result

        meeting = ScheduledMeeting.objects.create(
            thread=thread,
            lead_id=thread.lead_id,
            google_event_id=event.get("event_id") or "",
            html_link=event.get("html_link") or "",
            title=decision.meeting_title or "Sales call",
            start_at=_parse_start_dt(decision.start_iso),
            duration_minutes=decision.duration_minutes,
            lead_email=lead.get("email") or thread.to_email or "",
        )

        if thread.lead_id:
            publish_lead_status_update(thread.lead_id, "meeting_booked")

        result["event_created"] = True
        result["meeting"] = {
            "id": meeting.id,
            "event_id": meeting.google_event_id,
            "html_link": meeting.html_link,
            "start_at": meeting.start_at,
        }
        return result

    def schedule_thread(
        self,
        thread: EmailThread,
        *,
        start_iso: str | None = None,
        duration_minutes: int = 30,
        title: str = "",
    ) -> dict:
        """Manually book a meeting for a thread (uses last inbound message for context if needed)."""
        last_inbound = (
            thread.emails.filter(direction=SentEmail.Direction.INBOUND).order_by("-sent_at").first()
        )
        if not last_inbound and not start_iso:
            raise ExpectedError("no inbound message and no start_iso provided")

        lead = {
            "name": thread.name or "",
            "email": thread.to_email or "",
            "company_name": thread.company_name or "",
        }
        messages = [
            {"author": "lead", "body": last_inbound.body or ""} if last_inbound else None
        ]
        messages = [m for m in messages if m]

        if start_iso:
            if not calendar_configured():
                raise ExpectedError("Google Calendar is not configured")
            event = create_meeting_event(
                title=title or f"Call with {lead['name'] or lead['email']}",
                start_iso=start_iso,
                duration_minutes=duration_minutes,
                lead_email=lead["email"],
                lead_name=lead["name"],
                company_name=lead["company_name"],
            )
            meeting = ScheduledMeeting.objects.create(
                thread=thread,
                lead_id=thread.lead_id,
                google_event_id=event.get("event_id") or "",
                html_link=event.get("html_link") or "",
                title=title or "Sales call",
                start_at=_parse_start_dt(start_iso),
                duration_minutes=duration_minutes,
                lead_email=lead["email"],
            )
            if thread.lead_id:
                publish_lead_status_update(thread.lead_id, "meeting_booked")
            return {
                "event_created": True,
                "meeting": {
                    "id": meeting.id,
                    "event_id": meeting.google_event_id,
                    "html_link": meeting.html_link,
                    "start_at": meeting.start_at,
                },
            }

        from core.services.inbox import InboxService

        thread_messages = InboxService().build_thread_messages(thread)
        result = self.process_inbound(
            thread=thread,
            thread_messages=thread_messages,
            latest_message=last_inbound.body or "",
            lead=lead,
        )
        if result is None:
            raise ExpectedError("latest message does not indicate scheduling intent")
        if not result.get("event_created"):
            raise ExpectedError("could not book meeting — no confirmed time or calendar error")
        return result
