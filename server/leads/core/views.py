from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Lead
from core.permissions import InternalSecretOrAuthenticated
from core.serializers import LeadSerializer
from core.messaging import publish_research_request
from core.services.linkedin_csv_import_service import LinkedInConnectionsCsvImportService
from core.services.linkedin_lead_sync_service import LinkedInLeadSyncService


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

    @action(detail=False, methods=["get"], url_path="linkedin/lead-sync/auth-url")
    def linkedin_lead_sync_auth_url(self, request):
        svc = LinkedInLeadSyncService()
        payload = svc.build_authorize_url(user_id=request.user.id)
        return Response(payload, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="linkedin/lead-sync/exchange")
    def linkedin_lead_sync_exchange(self, request):
        code = (request.data or {}).get("code")
        svc = LinkedInLeadSyncService()
        conn = svc.connect(user_id=request.user.id, code=code)
        return Response(
            {
                "connected": bool(conn.access_token),
                "scope": conn.scope,
                "expires_at": conn.expires_at,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="linkedin/lead-sync/pull")
    def linkedin_lead_sync_pull(self, request):
        body = request.data or {}
        organization_urn = (body.get("organization_urn") or "").strip()
        sponsored_account_urn = (body.get("sponsored_account_urn") or "").strip()
        owner = {}
        if organization_urn:
            owner["organization"] = organization_urn
        if sponsored_account_urn:
            owner["sponsoredAccount"] = sponsored_account_urn
        if not owner:
            return Response(
                {"error": "Provide organization_urn or sponsored_account_urn."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        start = int(body.get("start") or 0)
        count = int(body.get("count") or 50)
        svc = LinkedInLeadSyncService()
        result = svc.pull_and_import(user_id=request.user.id, owner=owner, start=start, count=count)
        return Response(
            {
                "imported": result.imported,
                "skipped": result.skipped,
                "errors": result.errors,
                "next_start": result.next_start,
            },
            status=status.HTTP_200_OK,
        )