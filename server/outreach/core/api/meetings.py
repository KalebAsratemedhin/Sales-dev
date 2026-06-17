from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import ScheduledMeeting


def _meeting_dict(meeting: ScheduledMeeting) -> dict:
    thread = meeting.thread
    return {
        "id": meeting.id,
        "thread_id": meeting.thread_id,
        "lead_id": meeting.lead_id,
        "lead_name": thread.name or "",
        "lead_email": meeting.lead_email or thread.to_email or "",
        "company_name": thread.company_name or "",
        "title": meeting.title or "",
        "start_at": meeting.start_at.isoformat(),
        "duration_minutes": meeting.duration_minutes,
        "html_link": meeting.html_link or "",
        "google_event_id": meeting.google_event_id or "",
        "created_at": meeting.created_at.isoformat(),
    }


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def meeting_list(request):
    when = (request.query_params.get("when") or "all").strip().lower()
    if when not in {"upcoming", "past", "all"}:
        return Response({"error": "invalid when"}, status=status.HTTP_400_BAD_REQUEST)

    now = timezone.now()
    qs = ScheduledMeeting.objects.filter(thread__user_id=request.user.id).select_related("thread")

    if when == "upcoming":
        qs = qs.filter(start_at__gte=now).order_by("start_at")
    elif when == "past":
        qs = qs.filter(start_at__lt=now).order_by("-start_at")
    else:
        qs = qs.order_by("-start_at")

    try:
        page = max(1, int(request.query_params.get("page") or 1))
    except (TypeError, ValueError):
        return Response({"error": "invalid page"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        page_size = min(max(1, int(request.query_params.get("page_size") or 10)), 50)
    except (TypeError, ValueError):
        return Response({"error": "invalid page_size"}, status=status.HTTP_400_BAD_REQUEST)

    total = qs.count()
    offset = (page - 1) * page_size
    meetings = qs[offset : offset + page_size]

    return Response(
        {
            "items": [_meeting_dict(m) for m in meetings],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, (total + page_size - 1) // page_size),
        }
    )
