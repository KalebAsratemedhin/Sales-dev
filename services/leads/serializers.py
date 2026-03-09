from rest_framework import serializers
from .models import Lead, Persona


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            "id",
            "email",
            "name",
            "company_name",
            "company_website",
            "source",
            "profile_url",
            "persona",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "created_at", "updated_at")