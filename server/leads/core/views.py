from rest_framework import viewsets
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
            )

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        persona_id = self.request.query_params.get("persona_id")
        if status:
            qs = qs.filter(status=status)
        if persona_id:
            qs = qs.filter(persona_id=persona_id)
        return qs