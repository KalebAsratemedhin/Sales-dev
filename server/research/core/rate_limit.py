import os

from common.rate_limiter import RateLimitExceeded, acquire_token
from core.exceptions import TransientError

BUCKET_LLM_RESEARCH = "llm_research"


def rate_limit_llm_research() -> None:
    limit = int(os.environ.get("RATE_LIMIT_LLM_RESEARCH_PER_MINUTE", "30"))
    try:
        acquire_token(BUCKET_LLM_RESEARCH, limit)
    except RateLimitExceeded as e:
        raise TransientError(str(e)) from e
