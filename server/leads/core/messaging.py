from config.celery import app

from core.models import Lead


def handle_lead_status_update(payload):
    lead_id = payload.get("lead_id")
    new_status = (payload.get("status") or "").strip()
    if lead_id is None or not new_status:
        return
    if new_status not in dict(Lead.Status.choices):
        return
    Lead.objects.filter(pk=lead_id).update(status=new_status)


def _persona_payload(persona):
    if not persona:
        return {}
    return {
        "name": persona.name or "",
        "title_keywords": (persona.title_keywords or "")[:500],
        "industry_keywords": (persona.industry_keywords or "")[:500],
    }


def publish_research_request(
    lead_id,
    email,
    name,
    company_name,
    company_website,
    persona=None,
    user_id: int | None = None,
):
    payload = {
        "lead_id": lead_id,
        "email": email or "",
        "name": name or "",
        "company_name": company_name or "",
        "company_website": company_website or "",
        "persona": _persona_payload(persona),
        "user_id": user_id or 0,
    }
    app.send_task("research.run_research", args=[payload], queue="research")
