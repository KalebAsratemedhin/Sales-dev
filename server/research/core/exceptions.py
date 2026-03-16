

class TransientError(Exception):
    """Retryable failure (network, rate limit, 5xx). Consumer should nack."""


class ExpectedError(Exception):
    """Permanent failure (invalid payload, missing URL). Consumer should ack."""
