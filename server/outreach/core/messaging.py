import json
import os
import pika

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")


def handle_outreach_request(payload):
    print("Outreach request lead_id=%s email=%s" % (payload.get("lead_id"), payload.get("email")))


def run_consumer():
    conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    ch = conn.channel()
    ch.queue_declare(queue="outreach.request", durable=True)

    def on_message(ch, method, properties, body):
        try:
            payload = json.loads(body)
            handle_outreach_request(payload)
        except Exception as e:
            print("Error:", e)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue="outreach.request", on_message_callback=on_message)
    ch.start_consuming()


if __name__ == "__main__":
    run_consumer()