from django.urls import path
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.exceptions import ExpectedError, TransientError
from core.api import (
    config_detail,
    ingest_docs,
    activity_list,
    meeting_list,
    outreach_stats,
    run_followups,
    thread_detail,
    thread_draft_reply,
    thread_list,
    thread_send_reply,
    thread_schedule,
    google_auth_url,
    google_disconnect,
    google_exchange,
    google_settings,
    google_status,
    google_sync_n8n,
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
    path("api/outreach/activity/", activity_list),
    path("api/outreach/meetings/", meeting_list),
    path("api/outreach/threads/", thread_list),
    path("api/outreach/threads/<int:thread_id>/", thread_detail),
    path("api/outreach/threads/<int:thread_id>/draft/", thread_draft_reply),
    path("api/outreach/threads/<int:thread_id>/send/", thread_send_reply),
    path("api/outreach/threads/<int:thread_id>/schedule/", thread_schedule),
    path("api/outreach/google/status/", google_status),
    path("api/outreach/google/auth-url/", google_auth_url),
    path("api/outreach/google/exchange/", google_exchange),
    path("api/outreach/google/disconnect/", google_disconnect),
    path("api/outreach/google/settings/", google_settings),
    path("api/outreach/google/sync-n8n/", google_sync_n8n),
]
