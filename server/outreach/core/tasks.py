from config.celery import app

from core.exceptions import ExpectedError, TransientError
from core.services.outreach_email import run_outreach_from_payload


@app.task(name="outreach.run_outreach", bind=True, max_retries=5)
def run_outreach(self, payload):
    try:
        run_outreach_from_payload(payload)
    except ExpectedError as e:
        print("ExpectedError (drop outreach, no retry):", e)
        return
    except TransientError as e:
        countdown = min(60, 5 * (2 ** self.request.retries))
        raise self.retry(exc=e, countdown=countdown)


@app.task(name="outreach.send_followup", bind=True, max_retries=5)
def send_followup(self, thread_id):
    from core.services.followup import send_followup_for_thread

    try:
        send_followup_for_thread(thread_id)
    except ExpectedError as e:
        print("ExpectedError (drop followup, no retry):", e)
        return
    except TransientError as e:
        countdown = min(60, 5 * (2 ** self.request.retries))
        raise self.retry(exc=e, countdown=countdown)
