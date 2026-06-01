from config.celery import app

from core.exceptions import ExpectedError, TransientError
from core.services import run_research_from_payload


@app.task(name="research.run_research", bind=True, max_retries=5)
def run_research(self, payload):
    try:
        run_research_from_payload(payload)
    except ExpectedError as e:
        # Permanent failure (bad payload / missing URL): drop without retry.
        print("ExpectedError (drop research):", e)
        return
    except TransientError as e:
        # Retryable failure (network, rate limit, 5xx): exponential backoff.
        countdown = min(60, 5 * (2 ** self.request.retries))
        raise self.retry(exc=e, countdown=countdown)
