import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from common.google_api import get_google_api_key
from common.llm_errors import PERMANENT, classify_llm_error
from core.exceptions import ExpectedError, TransientError
from .prompts import ANALYZE_WEBSITE_PROMPT, build_analyze_website_prompt_context


def _raise_llm_error(exc: Exception) -> None:
    kind, message = classify_llm_error(exc)
    if kind == PERMANENT:
        raise ExpectedError(message) from exc
    raise TransientError(message) from exc


class WebsiteAnalysis(BaseModel):
    summary: str
    pain_points: list[str]
    use_cases: list[str]


def get_llm():
    api_key = get_google_api_key()

    return ChatGoogleGenerativeAI(
        model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        google_api_key=api_key,
        temperature=0.2,
        max_retries=0,
    )


def analyze_website(url: str, text: str, persona: dict | None = None) -> dict:
    """
    Run LLM analysis on website text.
    Returns dict with keys: summary, pain_points, use_cases, url.
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(WebsiteAnalysis)
    prompt = ChatPromptTemplate.from_messages([
        ("human", ANALYZE_WEBSITE_PROMPT),
    ])

    chain = prompt | structured_llm
    truncated = (text or "")[:15000]
    persona_block = build_analyze_website_prompt_context(persona or {})

    try:
        result = chain.invoke({
            "url": url,
            "text": truncated,
            "persona_block": persona_block,
        })
    except Exception as e:
        _raise_llm_error(e)

    return {
        "summary": result.summary,
        "pain_points": result.pain_points,
        "use_cases": result.use_cases,
        "url": url,
    }