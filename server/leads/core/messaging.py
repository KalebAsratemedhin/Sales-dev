import json
import os
import pika

from core.models import Lead

RABBITMQ_URL = os.environ.get("RABBITMQ_URL")
QUEUE_LEAD_STATUS_UPDATE = "lead.status.update"


def handle_lead_status_update(payload):
    lead_id = payload.get("lead_id")
    new_status = (payload.get("status") or "").strip()
    if lead_id is None or not new_status:
        return
    if new_status not in dict(Lead.Status.choices):
        return
    Lead.objects.filter(pk=lead_id).update(status=new_status)


def run_consumer():
    conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    ch = conn.channel()
    ch.queue_declare(queue=QUEUE_LEAD_STATUS_UPDATE, durable=True)

    def on_message(ch, method, properties, body):
        try:
            payload = json.loads(body)
            handle_lead_status_update(payload)
        except (json.JSONDecodeError, TypeError):
            pass
        ch.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue=QUEUE_LEAD_STATUS_UPDATE, on_message_callback=on_message)
    ch.start_consuming()


def _persona_payload(persona):
    if not persona:
        return {}
    return {
        "name": persona.name or "",
        "title_keywords": (persona.title_keywords or "")[:500],
        "industry_keywords": (persona.industry_keywords or "")[:500],
    }


def publish_research_request(lead_id, email, name, company_name, company_website, persona=None):
    payload = {
        "lead_id": lead_id,
        "email": email or "",
        "name": name or "",
        "company_name": company_name or "",
        "company_website": company_website or "",
        "persona": _persona_payload(persona),
    }
    conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    try:
        ch = conn.channel()
        ch.queue_declare(queue="research.request", durable=True)
        ch.basic_publish(
            exchange="",
            routing_key="research.request",
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2),
        )
    finally:
        conn.close()