from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import EmailThread, SentEmail


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def outreach_stats(request):
    user_id = request.user.id
    threads = EmailThread.objects.filter(user_id=user_id)
    emails = SentEmail.objects.filter(thread__user_id=user_id)

    today = timezone.now().date()
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
        recent.append(
            {
                "time": email.sent_at.strftime("%H:%M:%S"),
                "level": "SEND" if email.direction == SentEmail.Direction.OUTBOUND else "RECV",
                "msg": f"{email.direction} to {email.thread.to_email or email.thread.name or 'lead'}: "
                f"{(email.body or '')[:80]}",
            }
        )

    unread = (
        threads.annotate(
            inbound_count=Count("emails", filter=Q(emails__direction=SentEmail.Direction.INBOUND)),
            outbound_count=Count("emails", filter=Q(emails__direction=SentEmail.Direction.OUTBOUND)),
        )
        .filter(inbound_count__gt=0)
        .count()
    )

    return Response(
        {
            "threads_total": threads.count(),
            "emails_outbound": emails.filter(direction=SentEmail.Direction.OUTBOUND).count(),
            "emails_inbound": emails.filter(direction=SentEmail.Direction.INBOUND).count(),
            "outbound_today": outbound_today,
            "inbound_today": inbound_today,
            "unread_threads": unread,
            "recent_logs": recent,
        }
    )
