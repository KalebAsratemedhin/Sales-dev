import json
import os
import pika

RABBITMQ_URL = os.environ.get("RABBITMQ_URL")

def publish_research_request(lead_id, email, name, company_name, company_website):
    payload = {
        "lead_id": lead_id,
        "email": email or "",
        "name": name or "",
        "company_name": company_name or "",
        "company_website": company_website or "",
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