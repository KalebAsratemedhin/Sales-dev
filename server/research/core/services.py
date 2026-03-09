import requests
from core.utils import simple_extract_text
from core.models import Research
from agent.agent import analyze_website
from core.messaging import publish_outreach_request


def run_research_from_payload(payload):
    lead_id = payload.get("lead_id")
    url = (payload.get("company_website") or "").strip()
    if not url:
        return
    try:
        resp = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (compatible; SDRBot/1.0)"},
        )
        resp.raise_for_status()
        text = simple_extract_text(resp.text)
    except Exception:
        text = "(could not fetch or parse page)"
    result = analyze_website(url=url, text=text)
    Research.objects.update_or_create(
        lead_id=lead_id,
        defaults={
            "website_summary": result.get("summary", ""),
            "pain_points": result.get("pain_points", []),
            "use_cases": result.get("use_cases", []),
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