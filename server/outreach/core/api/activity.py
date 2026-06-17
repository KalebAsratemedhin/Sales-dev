from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import SentEmail


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def activity_list(request):
    try:
        page = max(1, int(request.query_params.get("page") or 1))
    except (TypeError, ValueError):
        return Response({"error": "invalid page"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        page_size = min(max(1, int(request.query_params.get("page_size") or 10)), 50)
    except (TypeError, ValueError):
        return Response({"error": "invalid page_size"}, status=status.HTTP_400_BAD_REQUEST)

    emails = SentEmail.objects.filter(thread__user_id=request.user.id).select_related("thread")
    total = emails.count()
    offset = (page - 1) * page_size

    items = []
    for email in emails.order_by("-sent_at")[offset : offset + page_size]:
        thread = email.thread
        items.append(
            {
                "time": email.sent_at.strftime("%H:%M:%S"),
                "action": "sent" if email.direction == SentEmail.Direction.OUTBOUND else "received",
                "lead_id": thread.lead_id,
                "lead_name": thread.name or "",
                "lead_email": thread.to_email or "",
            }
        )

    return Response(
        {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, (total + page_size - 1) // page_size),
        }
    )
