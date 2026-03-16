import json
import os

import pika

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from core.exceptions import ExpectedError, TransientError
from core.services import run_outreach_from_payload

from core.messaging.publish import RABBITMQ_URL


def run_consumer():
    conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    ch = conn.channel()
    ch.queue_declare(queue="outreach.request", durable=True)

    def on_message(ch, method, properties, body):
        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, TypeError) as e:
            print("Invalid outreach message:", e)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        try:
            run_outreach_from_payload(payload)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except ExpectedError as e:
            print("ExpectedError (ack outreach):", e)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except TransientError as e:
            print("TransientError (nack outreach):", e)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except Exception as e:
            print("Unexpected error (nack outreach):", e)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    ch.basic_consume(queue="outreach.request", on_message_callback=on_message)
    ch.start_consuming()


if __name__ == "__main__":
    run_consumer()
