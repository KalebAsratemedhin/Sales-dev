class TransientError(Exception):
    """Retryable failure (network, rate limit, external API)."""


class ExpectedError(Exception):
    """Permanent failure (invalid payload, bad status) that should be acked."""

