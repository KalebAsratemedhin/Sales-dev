import logging
from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger("auth_api")


def _safe_payload(payload: Any) -> str:
    try:
        return repr(payload)
    except Exception:
        return "<unprintable_payload>"


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    """
    DRF exception hook that logs auth failures with request context.
    Keeps the default DRF response payload so the frontend can rely on DRF's shape.
    """

    response = drf_exception_handler(exc, context)
    request = context.get("request")
    method = getattr(request, "method", "")
    path = getattr(request, "path", "")
    status_code = response.status_code if response is not None else status.HTTP_500_INTERNAL_SERVER_ERROR
    payload = getattr(response, "data", None) if response is not None else None

    if status_code >= 500:
        logger.exception(
            "Auth API exception %s %s status=%s payload=%s exc=%s",
            method,
            path,
            status_code,
            _safe_payload(payload),
            exc,
        )
    else:
        # For 4xx, avoid noisy stack traces but still capture meaningful details.
        message = exc if isinstance(exc, APIException) else str(exc)
        logger.warning(
            "Auth API exception %s %s status=%s payload=%s exc=%s",
            method,
            path,
            status_code,
            _safe_payload(payload),
            message,
        )

    if response is None:
        return Response(
            {"error": "internal_server_error", "detail": "Unexpected server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return response

