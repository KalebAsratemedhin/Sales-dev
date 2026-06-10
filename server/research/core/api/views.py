import os

import requests
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Research


def _research_dict(r: Research, lead: dict | None = None) -> dict:
    data = {
        "id": r.id,
        "lead_id": r.lead_id,
        "website_summary": r.website_summary or "",
        "pain_points": r.pain_points or [],
        "use_cases": r.use_cases or [],
        "raw_content_preview": r.raw_content_preview or "",
        "created_at": r.created_at.isoformat(),
    }
    if lead:
        data.update(
            {
                "lead_name": lead.get("name") or "",
                "lead_email": lead.get("email") or "",
                "company_name": lead.get("company_name") or "",
                "lead_status": lead.get("status") or "",
            }
        )
    return data


def _user_leads(request) -> tuple[list[dict], Response | None]:
    leads_base = (os.environ.get("LEADS_SERVICE_URL") or "http://leads:8001").rstrip("/")
    auth = request.headers.get("Authorization") or ""
    try:
        resp = requests.get(
            f"{leads_base}/api/leads/",
            headers={"Authorization": auth},
            timeout=15,
        )
    except requests.RequestException as e:
        return [], Response({"error": f"leads service unavailable: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if resp.status_code >= 400:
        return [], Response({"error": "failed to load leads"}, status=status.HTTP_502_BAD_GATEWAY)

    payload = resp.json()
    if isinstance(payload, dict):
        leads = payload.get("results") or []
    else:
        leads = payload
    return leads, None


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def research_list(request):
    leads, err = _user_leads(request)
    if err is not None:
        return err

    lead_by_id = {lead["id"]: lead for lead in leads if lead.get("id") is not None}
    if not lead_by_id:
        return Response([])

    qs = Research.objects.filter(lead_id__in=lead_by_id.keys()).order_by("-created_at")[:200]
    return Response([_research_dict(r, lead_by_id.get(r.lead_id)) for r in qs])


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def research_by_lead(request, lead_id: int):
    research = Research.objects.filter(lead_id=lead_id).first()
    if research is None:
        return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(_research_dict(research))


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def research_stats(request):
    total = Research.objects.count()
    today_count = Research.objects.filter(created_at__date=timezone.now().date()).count()

    recent_logs = []
    for r in Research.objects.order_by("-created_at")[:15]:
        preview = (r.raw_content_preview or r.website_summary or "")[:80]
        recent_logs.append(
            {
                "time": r.created_at.strftime("%H:%M:%S"),
                "level": "SCAN",
                "msg": f"Research complete for lead #{r.lead_id}: {preview}",
            }
        )

    return Response(
        {
            "total": total,
            "today": today_count,
            "recent_logs": recent_logs,
        }
    )
