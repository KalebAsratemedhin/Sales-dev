from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Lead
from core.serializers import LeadSerializer
from core.messaging import publish_research_request


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all().order_by("-created_at")
    serializer_class = LeadSerializer

    def perform_create(self, serializer):
        lead = serializer.save()
        if lead.company_website:
            publish_research_request(
                lead.id,
                lead.email,
                lead.name,
                lead.company_name,
                lead.company_website,
                persona=getattr(lead, "persona", None) and lead.persona,
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
        status = self.request.query_params.get("status")
        persona_id = self.request.query_params.get("persona_id")
        if status:
            qs = qs.filter(status=status)
        if persona_id:
            qs = qs.filter(persona_id=persona_id)
        return qs