import os
from datetime import datetime, timezone

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from agent.agent import _raise_llm_error
from common.google_api import get_google_api_key


SCHEDULING_PROMPT = """You are a meeting-scheduling assistant for an SDR.

Lead:
- Name: {lead_name}
- Email: {lead_email}
- Company: {company_name}

Thread (most recent last):
---
{thread_messages_block}
---

Latest message from the lead:
---
{latest_message}
---

Current UTC time: {current_utc}

Calendly link (fallback if no specific time agreed): {calendly_link}

Decide how to respond:
1. If the lead proposes or confirms a specific date/time → set scheduling_relevant=true, ready_to_book=true, and fill start_iso (ISO8601 with timezone, must be in the future).
2. If the lead wants a call but no time is agreed → scheduling_relevant=true, ready_to_book=false; ask for their availability or share the Calendly link.
3. Otherwise → scheduling_relevant=false, ready_to_book=false.

Write reply_body as the email reply (no subject). If booking, confirm the time clearly. Use blank lines between paragraphs.
Do NOT include a signature/footer.
"""


class SchedulingDecision(BaseModel):
    scheduling_relevant: bool = Field(description="Lead wants to schedule or discuss a meeting")
    ready_to_book: bool = Field(description="A specific future date/time is agreed and can be booked now")
    start_iso: str = Field(default="", description="ISO8601 start time when ready_to_book is true")
    duration_minutes: int = Field(default=30, description="Meeting length in minutes")
    meeting_title: str = Field(default="", description="Short calendar event title")
    reply_body: str = Field(description="Email reply to send to the lead")


def _get_llm():
    return ChatGoogleGenerativeAI(
        model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        google_api_key=get_google_api_key(),
        temperature=0.2,
        max_retries=0,
    )


def run_scheduling_agent(
    *,
    thread_messages: list[dict],
    latest_message: str,
    lead: dict,
    calendly_link: str = "",
) -> SchedulingDecision:
    if thread_messages:
        block = "\n".join(
            f"{m.get('author') or 'Unknown'}: {m.get('body') or ''}" for m in thread_messages
        )
    else:
        block = "(no previous messages)"

    prompt = ChatPromptTemplate.from_messages([("human", SCHEDULING_PROMPT)])
    chain = prompt | _get_llm().with_structured_output(SchedulingDecision)

    try:
        return chain.invoke(
            {
                "lead_name": lead.get("name") or "",
                "lead_email": lead.get("email") or "",
                "company_name": lead.get("company_name") or "",
                "thread_messages_block": block,
                "latest_message": latest_message or "",
                "current_utc": datetime.now(timezone.utc).isoformat(),
                "calendly_link": calendly_link or "(none)",
            }
        )
    except Exception as e:
        _raise_llm_error(e)
