import os

import requests
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Lead
from core.permissions import InternalSecretOrAuthenticated
from core.serializers import LeadSerializer
from core.messaging import publish_outreach_request, publish_research_request
from core.services.linkedin_csv_import_service import LinkedInConnectionsCsvImportService


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all().order_by("-created_at")
    serializer_class = LeadSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [InternalSecretOrAuthenticated]

    def perform_create(self, serializer):
        lead = serializer.save(
            user=self.request.user if getattr(self.request.user, "is_authenticated", False) else None
        )
        if lead.company_website:
            publish_research_request(
                lead.id,
                lead.email,
                lead.name,
                lead.company_name,
                lead.company_website,
                persona=getattr(lead, "persona", None) and lead.persona,
                user_id=lead.user_id or 0,
            )

    @action(detail=True, methods=["post"], url_path="set_status")
    def set_status(self, request, pk=None):
        secret = getattr(settings, "LEADS_SERVICE_INTERNAL_SECRET", None)
        if secret and request.headers.get("X-Internal-Secret") != secret:
            return Response(status=status.HTTP_403_FORBIDDEN)

        lead = self.get_object()
        new_status = (request.data or {}).get("status")
        if not new_status or new_status not in dict(Lead.Status.choices):
            return Response(
                {"error": "invalid or missing status"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        lead.status = new_status
        lead.save(update_fields=["status", "updated_at"])
        return Response({"status": lead.status})

    def get_queryset(self):
        qs = super().get_queryset()
        secret = getattr(settings, "LEADS_SERVICE_INTERNAL_SECRET", None)
        is_internal = bool(secret and self.request.headers.get("X-Internal-Secret") == secret)
        if not is_internal:
            if not getattr(self.request.user, "is_authenticated", False):
                qs = qs.none()
            else:
                qs = qs.filter(user=self.request.user)

        status = self.request.query_params.get("status")
        persona_id = self.request.query_params.get("persona_id")
        if status:
            qs = qs.filter(status=status)
        if persona_id:
            qs = qs.filter(persona_id=persona_id)
        return qs

    @action(detail=True, methods=["post"], url_path="send-outreach")
    def send_outreach(self, request, pk=None):
        lead = self.get_object()
        if not (lead.email or "").strip():
            return Response({"error": "lead has no email"}, status=status.HTTP_400_BAD_REQUEST)

        research_base = (os.environ.get("RESEARCH_SERVICE_URL") or "http://research:8002").rstrip("/")
        auth = request.headers.get("Authorization") or ""
        try:
            resp = requests.get(
                f"{research_base}/api/research/leads/{lead.id}/",
                headers={"Authorization": auth},
                timeout=15,
            )
        except requests.RequestException as e:
            return Response({"error": f"research service unavailable: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if resp.status_code == 404:
            return Response({"error": "research not found"}, status=status.HTTP_400_BAD_REQUEST)
        if resp.status_code >= 400:
            return Response({"error": "failed to load research"}, status=status.HTTP_502_BAD_GATEWAY)

        research = resp.json()
        publish_outreach_request(
            lead_id=lead.id,
            email=lead.email,
            name=lead.name,
            company_name=lead.company_name,
            company_website=lead.company_website,
            research_summary=research.get("website_summary") or "",
            pain_points=research.get("pain_points") or [],
            use_cases=research.get("use_cases") or [],
            persona=lead.persona,
            user_id=lead.user_id or 0,
        )
        return Response({"queued": True}, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["post"], url_path="import/linkedin-connections")
    def import_linkedin_connections_csv(self, request):
        upload = request.FILES.get("file")
        if not upload:
            return Response({"error": "Missing file field 'file'."}, status=status.HTTP_400_BAD_REQUEST)

        raw = upload.read()
        svc = LinkedInConnectionsCsvImportService()
        result = svc.import_file(
            user_id=getattr(getattr(request, "user", None), "id", None),
            file_bytes=raw,
        )
        return Response(
            {
                "created": result.created,
                "updated": result.updated,
                "skipped": result.skipped,
                "errors": result.errors,
            },
            status=status.HTTP_200_OK,
        )
