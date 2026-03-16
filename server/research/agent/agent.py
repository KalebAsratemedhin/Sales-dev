import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from core.exceptions import TransientError
from .prompts import ANALYZE_WEBSITE_PROMPT, build_analyze_website_prompt_context


class WebsiteAnalysis(BaseModel):
    summary: str
    pain_points: list[str]
    use_cases: list[str]


def get_llm():
    api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")

    return ChatGoogleGenerativeAI(
        model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        google_api_key=api_key,
        temperature=0.2,
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
        raise TransientError(str(e)) from e

    return {
        "summary": result.summary,
        "pain_points": result.pain_points,
        "use_cases": result.use_cases,
        "url": url,
    }