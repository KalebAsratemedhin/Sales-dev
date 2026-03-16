import os

from core.exceptions import ExpectedError
from core.extraction import gather_site_text
from core.messaging import publish_lead_status_update, publish_outreach_request
from core.models import Research
from core.utils import run_with_retries
from agent.agent import analyze_website

RAW_CONTENT_PREVIEW_MAX = 2000
LLM_RETRIES = 3
LLM_BACKOFF_BASE = 2.0


def _persona_from_payload(payload):
    p = payload.get("persona") or {}
    return {
        "name": p.get("name") or "",
        "title_keywords": p.get("title_keywords") or "",
        "industry_keywords": p.get("industry_keywords") or "",
    }


def _republish_outreach_for_existing(payload, research):
    publish_outreach_request(
        lead_id=payload.get("lead_id"),
        email=payload.get("email", ""),
        name=payload.get("name", ""),
        company_name=payload.get("company_name", ""),
        company_website=payload.get("company_website", ""),
        research_summary=research.website_summary,
        pain_points=research.pain_points,
        use_cases=research.use_cases,
    )


def run_research_from_payload(payload):
    lead_id = payload.get("lead_id")
    url = (payload.get("company_website") or "").strip()

    if not url:
        raise ExpectedError("missing company_website")

    if lead_id is None:
        raise ExpectedError("missing lead_id")

    existing = Research.objects.filter(lead_id=lead_id).first()
    if existing and not payload.get("force"):
        _republish_outreach_for_existing(payload, existing)
        return

    max_extra_pages = 2 if os.environ.get("RESEARCH_MULTI_PAGE", "").strip().lower() in ("1", "true", "yes") else 0
    text = gather_site_text(url, max_extra_pages=max_extra_pages)
    raw_preview = (text or "")[:RAW_CONTENT_PREVIEW_MAX]
    persona = _persona_from_payload(payload)

    result = run_with_retries(
        analyze_website,
        retries=LLM_RETRIES,
        backoff_base=LLM_BACKOFF_BASE,
        url=url,
        text=text,
        persona=persona,
    )

    Research.objects.update_or_create(
        lead_id=lead_id,
        defaults={
            "website_summary": result.get("summary", ""),
            "pain_points": result.get("pain_points", []),
            "use_cases": result.get("use_cases", []),
            "raw_content_preview": raw_preview,
        },
    )

    publish_outreach_request(
        lead_id=lead_id,
        email=payload.get("email", ""),
        name=payload.get("name", ""),
        company_name=payload.get("company_name", ""),
        company_website=url,
        research_summary=result.get("summary", ""),
        pain_points=result.get("pain_points", []),
        use_cases=result.get("use_cases", []),
    )

    publish_lead_status_update(lead_id, "researched")
