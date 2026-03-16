import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from core.exceptions import TransientError
from .prompts import (
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
    api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")

    return ChatGoogleGenerativeAI(
        model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        google_api_key=api_key,
        temperature=0.4,
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
        raise TransientError(str(e)) from e

    return {
        "subject": result.subject,
        "body": result.body,
    }


def handle_inbox_reply(
    thread_messages: list[dict],
    new_message: dict,
    lead: dict,
    research: dict,
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

    docs_snippets = search_product_docs(latest_message, max_results=3)
    if docs_snippets:
        docs_block = "\n\n".join(snippet["snippet"] for snippet in docs_snippets)
    else:
        docs_block = "(no docs found)"

    calendly_link = get_calendly_link(lead.get("email"))

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
        raise TransientError(str(e)) from e

    return {
        "reply_body": result.body,
        "calendly_link": calendly_link,
    }

