from django.db.models import Count, F, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.exceptions import ExpectedError, TransientError
from core.models import EmailThread, SentEmail
from core.services.outreach_email import send_email
from core.services.inbox import InboxService
from core.services.scheduling import SchedulingService


def _preview(body: str, limit: int = 160) -> str:
    text = (body or "").replace("\n", " ").strip()
    return text[:limit] + ("…" if len(text) > limit else "")


def _thread_summary(thread: EmailThread) -> dict:
    last_email = thread.emails.order_by("-sent_at").first()
    inbound = thread.emails.filter(direction=SentEmail.Direction.INBOUND).count()
    outbound = thread.emails.filter(direction=SentEmail.Direction.OUTBOUND).count()
    return {
        "id": thread.id,
        "lead_id": thread.lead_id,
        "name": thread.name or "",
        "to_email": thread.to_email or "",
        "subject": thread.subject or "",
        "company_name": thread.company_name or "",
        "last_message_at": (thread.last_message_at or thread.created_at).isoformat(),
        "preview": _preview(last_email.body if last_email else ""),
        "has_inbound": inbound > 0,
        "unread": inbound > outbound,
        "message_count": thread.emails.count(),
    }


def _message_dict(email: SentEmail) -> dict:
    return {
        "id": email.id,
        "thread_id": email.thread_id,
        "direction": email.direction,
        "body": email.body or "",
        "sent_at": email.sent_at.isoformat(),
        "message_id": email.message_id or "",
    }


def _user_threads(request):
    return EmailThread.objects.filter(user_id=request.user.id)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def thread_list(request):
    qs = _user_threads(request).order_by("-last_message_at", "-created_at")

    lead_id = request.query_params.get("lead_id")
    if lead_id:
        try:
            qs = qs.filter(lead_id=int(lead_id))
        except (TypeError, ValueError):
            return Response({"error": "invalid lead_id"}, status=status.HTTP_400_BAD_REQUEST)

    filter_param = (request.query_params.get("filter") or "all").strip().lower()
    if filter_param == "unread":
        qs = qs.annotate(
            inbound_count=Count("emails", filter=Q(emails__direction=SentEmail.Direction.INBOUND)),
            outbound_count=Count("emails", filter=Q(emails__direction=SentEmail.Direction.OUTBOUND)),
        ).filter(inbound_count__gt=F("outbound_count"))
    elif filter_param == "archived":
        qs = qs.filter(to_email="")

    return Response([_thread_summary(t) for t in qs[:200]])


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def thread_detail(request, thread_id: int):
    thread = _user_threads(request).filter(pk=thread_id).first()
    if thread is None:
        return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)

    data = _thread_summary(thread)
    data.update(
        {
            "research_summary": thread.research_summary or "",
            "pain_points": thread.pain_points or [],
            "use_cases": thread.use_cases or [],
            "gmail_thread_id": thread.gmail_thread_id or "",
            "messages": [_message_dict(e) for e in thread.emails.order_by("sent_at")],
            "meetings": [
                {
                    "id": m.id,
                    "title": m.title,
                    "start_at": m.start_at.isoformat(),
                    "duration_minutes": m.duration_minutes,
                    "html_link": m.html_link,
                    "lead_email": m.lead_email,
                }
                for m in thread.meetings.all()[:10]
            ],
        }
    )
    return Response(data)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def thread_draft_reply(request, thread_id: int):
    """Generate an AI reply draft without recording a new inbound message."""
    thread = _user_threads(request).filter(pk=thread_id).first()
    if thread is None:
        return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)

    svc = InboxService()
    try:
        result = svc.draft_reply_for_thread(thread)
    except ExpectedError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"body": result.get("reply_body") or ""})


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def thread_send_reply(request, thread_id: int):
    thread = _user_threads(request).filter(pk=thread_id).first()
    if thread is None:
        return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)

    body = (request.data.get("body") or "").strip()
    if not body:
        return Response({"error": "body is required"}, status=status.HTTP_400_BAD_REQUEST)

    to_email = (thread.to_email or "").strip()
    if not to_email:
        return Response({"error": "thread has no recipient email"}, status=status.HTTP_400_BAD_REQUEST)

    subject = (thread.subject or "Re: follow up").strip()
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"

    try:
        message_id, gmail_thread_id, formatted_body = send_email(to_email, subject, body)
    except ExpectedError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except TransientError as e:
        return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if not gmail_thread_id:
        gmail_thread_id = thread.gmail_thread_id or ""

    if gmail_thread_id and not thread.gmail_thread_id:
        thread.gmail_thread_id = gmail_thread_id
        thread.save(update_fields=["gmail_thread_id"])

    SentEmail.objects.create(
        thread=thread,
        message_id=message_id,
        direction=SentEmail.Direction.OUTBOUND,
        body=formatted_body,
    )
    thread.last_message_at = timezone.now()
    thread.save(update_fields=["last_message_at", "gmail_thread_id"])

    return Response({"sent": True, "message_id": message_id})


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def thread_schedule(request, thread_id: int):
    """Book a Google Calendar meeting for this thread and invite the lead."""
    thread = _user_threads(request).filter(pk=thread_id).first()
    if thread is None:
        return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data or {}
    try:
        result = SchedulingService().schedule_thread(
            thread,
            start_iso=(data.get("start_iso") or "").strip() or None,
            duration_minutes=int(data.get("duration_minutes") or 30),
            title=(data.get("title") or "").strip(),
        )
    except ExpectedError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except TransientError as e:
        return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response(result, status=status.HTTP_201_CREATED)
