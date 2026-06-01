from config.celery import app

from core.messaging import handle_lead_status_update


@app.task(name="leads.update_status")
def update_status(payload):
    handle_lead_status_update(payload)
