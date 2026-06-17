from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import EmailThread, ScheduledMeeting, SentEmail


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def outreach_stats(request):
    user_id = request.user.id
    threads = EmailThread.objects.filter(user_id=user_id)
    emails = SentEmail.objects.filter(thread__user_id=user_id)

    today = timezone.now().date()
    now = timezone.now()
    outbound_today = emails.filter(
        direction=SentEmail.Direction.OUTBOUND,
        sent_at__date=today,
    ).count()
    inbound_today = emails.filter(
        direction=SentEmail.Direction.INBOUND,
        sent_at__date=today,
    ).count()

    recent = []
    for email in emails.select_related("thread").order_by("-sent_at")[:15]:
        thread = email.thread
        recent.append(
            {
                "time": email.sent_at.strftime("%H:%M:%S"),
                "action": "sent" if email.direction == SentEmail.Direction.OUTBOUND else "received",
                "lead_id": thread.lead_id,
                "lead_name": thread.name or "",
                "lead_email": thread.to_email or "",
            }
        )

    meetings = ScheduledMeeting.objects.filter(thread__user_id=user_id)
    meetings_upcoming = meetings.filter(start_at__gte=now).count()
    meetings_past = meetings.filter(start_at__lt=now).count()
    meetings_today = meetings.filter(start_at__date=today).count()
    next_meeting = (
        meetings.filter(start_at__gte=now)
        .select_related("thread")
        .order_by("start_at")
        .first()
    )

    unread = (
        threads.annotate(
            inbound_count=Count("emails", filter=Q(emails__direction=SentEmail.Direction.INBOUND)),
            outbound_count=Count("emails", filter=Q(emails__direction=SentEmail.Direction.OUTBOUND)),
        )
        .filter(inbound_count__gt=0)
        .count()
    )

    email_activity_7d = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        email_activity_7d.append(
            {
                "date": day.isoformat(),
                "label": day.strftime("%a"),
                "sent": emails.filter(
                    direction=SentEmail.Direction.OUTBOUND,
                    sent_at__date=day,
                ).count(),
                "received": emails.filter(
                    direction=SentEmail.Direction.INBOUND,
                    sent_at__date=day,
                ).count(),
            }
        )

    return Response(
        {
            "threads_total": threads.count(),
            "emails_outbound": emails.filter(direction=SentEmail.Direction.OUTBOUND).count(),
            "emails_inbound": emails.filter(direction=SentEmail.Direction.INBOUND).count(),
            "outbound_today": outbound_today,
            "inbound_today": inbound_today,
            "unread_threads": unread,
            "meetings_upcoming": meetings_upcoming,
            "meetings_past": meetings_past,
            "meetings_today": meetings_today,
            "next_meeting": (
                {
                    "id": next_meeting.id,
                    "title": next_meeting.title,
                    "start_at": next_meeting.start_at.isoformat(),
                    "lead_name": next_meeting.thread.name or "",
                    "lead_email": next_meeting.lead_email or next_meeting.thread.to_email or "",
                    "html_link": next_meeting.html_link or "",
                }
                if next_meeting
                else None
            ),
            "recent_logs": recent,
            "email_activity_7d": email_activity_7d,
        }
    )
