import json
import os

import pika

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")


def publish_lead_status_update(lead_id, status):
    payload = {"lead_id": lead_id, "status": status}
    conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    try:
        ch = conn.channel()
        ch.queue_declare(queue="lead.status.update", durable=True)
        ch.basic_publish(
            exchange="",
            routing_key="lead.status.update",
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2),
        )
    finally:
        conn.close()
