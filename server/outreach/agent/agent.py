import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from common.google_api import get_google_api_key
from common.llm_errors import PERMANENT, classify_llm_error
from core.exceptions import ExpectedError, TransientError


def _raise_llm_error(exc: Exception) -> None:
    kind, message = classify_llm_error(exc)
    if kind == PERMANENT:
        raise ExpectedError(message) from exc
    raise TransientError(message) from exc
from .prompts import (
    FOLLOWUP_EMAIL_PROMPT,
    INBOX_REPLY_PROMPT,
    OUTREACH_EMAIL_PROMPT,
    build_list_block,
    build_persona_block,
)
from .tools import get_calendly_link, search_product_docs


class OutreachDraft(BaseModel):
    subject: str
    body: str


class InboxReply(BaseModel):
    body: str


def get_llm():
    api_key = get_google_api_key()

    return ChatGoogleGenerativeAI(
        model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        google_api_key=api_key,
        temperature=0.4,
        max_retries=0,
    )


def draft_outreach_email(lead: dict, research: dict, persona: dict | None = None) -> dict:
    llm = get_llm()
    structured_llm = llm.with_structured_output(OutreachDraft)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("human", OUTREACH_EMAIL_PROMPT),
        ]
    )

    chain = prompt | structured_llm

    pain_points_block = build_list_block(research.get("pain_points") or [], "pain points")
    use_cases_block = build_list_block(research.get("use_cases") or [], "use cases")
    persona_block = build_persona_block(persona or {})

    try:
        result = chain.invoke(
            {
                "lead_name": lead.get("name") or "",
                "lead_email": lead.get("email") or "",
                "company_name": lead.get("company_name") or "",
                "company_website": lead.get("company_website") or "",
                "research_summary": research.get("website_summary") or research.get("research_summary") or "",
                "pain_points_block": pain_points_block,
                "use_cases_block": use_cases_block,
                "persona_block": persona_block,
            }
        )
    except Exception as e:
        _raise_llm_error(e)

    return {
        "subject": result.subject,
        "body": result.body,
    }


def draft_followup_email(lead: dict, research: dict, thread_messages: list[dict]) -> dict:
    llm = get_llm()
    structured_llm = llm.with_structured_output(OutreachDraft)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("human", FOLLOWUP_EMAIL_PROMPT),
        ]
    )

    chain = prompt | structured_llm

    pain_points_block = build_list_block(research.get("pain_points") or [], "pain points")
    if thread_messages:
        thread_messages_block = "\n".join(
            f"{msg.get('author') or 'Unknown'}: {msg.get('body') or ''}" for msg in thread_messages
        )
    else:
        thread_messages_block = "(no previous messages)"

    try:
        result = chain.invoke(
            {
                "lead_name": lead.get("name") or "",
                "company_name": lead.get("company_name") or "",
                "research_summary": research.get("website_summary") or research.get("research_summary") or "",
                "pain_points_block": pain_points_block,
                "thread_messages_block": thread_messages_block,
            }
        )
    except Exception as e:
        _raise_llm_error(e)

    return {
        "subject": result.subject,
        "body": result.body,
    }


def handle_inbox_reply(
    thread_messages: list[dict],
    new_message: dict,
    lead: dict,
    research: dict,
    user_id: int = 0,
) -> dict:
    llm = get_llm()
    structured_llm = llm.with_structured_output(InboxReply)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("human", INBOX_REPLY_PROMPT),
        ]
    )

    chain = prompt | structured_llm

    thread_messages_block = ""
    if thread_messages:
        lines = []
        for msg in thread_messages:
            author = msg.get("author") or "Unknown"
            body = msg.get("body") or ""
            lines.append(f"{author}: {body}")
        thread_messages_block = "\n".join(lines)
    else:
        thread_messages_block = "(no previous messages)"

    latest_message = new_message.get("body") or ""

    docs_snippets = search_product_docs(latest_message, max_results=3, user_id=user_id)
    if docs_snippets:
        docs_block = "\n\n".join(snippet["snippet"] for snippet in docs_snippets)
    else:
        docs_block = "(no docs found)"

    calendly_link = get_calendly_link(user_id)

    try:
        result = chain.invoke(
            {
                "lead_email": lead.get("email") or "",
                "company_name": lead.get("company_name") or "",
                "thread_messages_block": thread_messages_block,
                "latest_message": latest_message,
                "docs_block": docs_block,
                "calendly_link": calendly_link or "(none)",
            }
        )
    except Exception as e:
        _raise_llm_error(e)

    return {
        "reply_body": result.body,
        "calendly_link": calendly_link,
    }

