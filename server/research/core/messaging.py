import json
import os
import pika

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from core.services import run_research_from_payload

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")


def publish_outreach_request(
    lead_id, email, name, company_name, company_website,
    research_summary, pain_points, use_cases,
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
    }
    conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    try:
        ch = conn.channel()
        ch.queue_declare(queue="outreach.request", durable=True)
        ch.basic_publish(
            exchange="",
            routing_key="outreach.request",
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2),
        )
    finally:
        conn.close()


def run_consumer():
    conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    ch = conn.channel()
    ch.queue_declare(queue="research.request", durable=True)

    def on_message(ch, method, properties, body):
        try:
            payload = json.loads(body)
            run_research_from_payload(payload)
        except Exception as e:
            print("Error processing message:", e)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue="research.request", on_message_callback=on_message)
    ch.start_consuming()


if __name__ == "__main__":
    run_consumer()