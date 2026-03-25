import json
import os

import pika

RABBITMQ_URL = os.environ.get("RABBITMQ_URL")
QUEUE_LINKEDIN_SYNC_PROFILE = "linkedin.sync.profile"


def publish_linkedin_sync_profile(payload: dict) -> None:
    conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    try:
        ch = conn.channel()
        ch.queue_declare(queue=QUEUE_LINKEDIN_SYNC_PROFILE, durable=True)
        ch.basic_publish(
            exchange="",
            routing_key=QUEUE_LINKEDIN_SYNC_PROFILE,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2),
        )
    finally:
        conn.close()

