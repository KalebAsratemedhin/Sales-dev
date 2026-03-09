import requests
from django.db import transaction

from services.agent.agent import analyze_website
from services.leads.models import Lead

from .models import Research
from .utils import simple_extract_text


def run_research(lead_id: int) -> None:
    """
    Load lead, fetch company website, run agent analysis, save Research, set lead status,
    and enqueue draft_and_send_email.
    """
    try:
        lead = Lead.objects.get(pk=lead_id)
    except Lead.DoesNotExist:
        return

    url = (lead.company_website or "").strip()
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

    with transaction.atomic():
        research, _ = Research.objects.update_or_create(
            lead_id=lead_id,
            defaults={
                "website_summary": result.get("summary", ""),
                "pain_points": result.get("pain_points", []),
                "use_cases": result.get("use_cases", []),
            },
        )
        lead.status = Lead.Status.RESEARCHED
        lead.save(update_fields=["status", "updated_at"])

    from services.outreach.tasks import draft_and_send_email
    draft_and_send_email.delay(lead_id)