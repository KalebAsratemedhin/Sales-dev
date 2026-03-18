from django.urls import path
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.exceptions import ExpectedError, TransientError
from core.api import config_detail, ingest_docs
from core.services.inbox import handle_inbox_reply_from_http


@api_view(["POST"])
def handle_reply(request):
    data = request.data or {}

    try:
        result = handle_inbox_reply_from_http(data)
    except ExpectedError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except TransientError as e:
        return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception:
        return Response({"error": "unexpected_error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(result)


urlpatterns = [
    path("api/outreach/config/", config_detail),
    path("api/outreach/ingest-docs/", ingest_docs),
    path("api/outreach/handle-reply/", handle_reply),
]