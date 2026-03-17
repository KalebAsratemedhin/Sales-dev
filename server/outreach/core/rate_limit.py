import os

from common.rate_limiter import RateLimitExceeded, acquire_token
from core.exceptions import TransientError

BUCKET_GMAIL = "gmail_outbound"
BUCKET_LLM_OUTREACH = "llm_outreach"


def _acquire(bucket: str, env_key: str, default: int) -> None:
    limit = int(os.environ.get(env_key, str(default)))
    try:
        acquire_token(bucket, limit)
    except RateLimitExceeded as e:
        raise TransientError(str(e)) from e


def rate_limit_gmail() -> None:
    _acquire(BUCKET_GMAIL, "RATE_LIMIT_GMAIL_PER_MINUTE", 60)


def rate_limit_llm_outreach() -> None:
    _acquire(BUCKET_LLM_OUTREACH, "RATE_LIMIT_LLM_OUTREACH_PER_MINUTE", 30)
