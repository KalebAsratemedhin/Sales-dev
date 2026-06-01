from config.celery import app


def publish_lead_status_update(lead_id, status):
    payload = {"lead_id": lead_id, "status": status}
    app.send_task("leads.update_status", args=[payload], queue="leads")


def publish_outreach_request(
    lead_id,
    email,
    name,
    company_name,
    company_website,
    research_summary,
    pain_points,
    use_cases,
    user_id: int | None = None,
):
    payload = {
        "lead_id": lead_id,
        "email": email,
        "name": name,
        "company_name": company_name,
        "company_website": company_website,
        "research_summary": research_summary,
        "pain_points": pain_points,
        "use_cases": use_cases,
        "user_id": user_id or 0,
    }
    app.send_task("outreach.run_outreach", args=[payload], queue="outreach")
