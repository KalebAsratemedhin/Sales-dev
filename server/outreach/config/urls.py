from django.urls import path
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.exceptions import ExpectedError, TransientError
from core.api import (
    config_detail,
    ingest_docs,
    outreach_stats,
    run_followups,
    thread_detail,
    thread_draft_reply,
    thread_list,
    thread_send_reply,
    thread_schedule,
    calendar_auth_url,
    calendar_disconnect,
    calendar_exchange,
    calendar_settings,
    calendar_status,
    gmail_auth_url,
    gmail_disconnect,
    gmail_exchange,
    gmail_status,
    gmail_sync_n8n,
)
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
    path("api/outreach/run-followups/", run_followups),
    path("api/outreach/stats/", outreach_stats),
    path("api/outreach/threads/", thread_list),
    path("api/outreach/threads/<int:thread_id>/", thread_detail),
    path("api/outreach/threads/<int:thread_id>/draft/", thread_draft_reply),
    path("api/outreach/threads/<int:thread_id>/send/", thread_send_reply),
    path("api/outreach/threads/<int:thread_id>/schedule/", thread_schedule),
    path("api/outreach/calendar/status/", calendar_status),
    path("api/outreach/calendar/auth-url/", calendar_auth_url),
    path("api/outreach/calendar/exchange/", calendar_exchange),
    path("api/outreach/calendar/disconnect/", calendar_disconnect),
    path("api/outreach/calendar/settings/", calendar_settings),
    path("api/outreach/gmail/status/", gmail_status),
    path("api/outreach/gmail/auth-url/", gmail_auth_url),
    path("api/outreach/gmail/exchange/", gmail_exchange),
    path("api/outreach/gmail/disconnect/", gmail_disconnect),
    path("api/outreach/gmail/sync-n8n/", gmail_sync_n8n),
]