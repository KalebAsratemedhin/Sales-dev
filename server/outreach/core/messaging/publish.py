from config.celery import app


def publish_lead_status_update(lead_id, status):
    payload = {"lead_id": lead_id, "status": status}
    app.send_task("leads.update_status", args=[payload], queue="leads")
