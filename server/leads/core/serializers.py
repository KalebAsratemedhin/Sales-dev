from rest_framework import serializers
from core.models import Lead, Persona


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ("id", "name", "title_keywords", "industry_keywords", "search_keywords", "is_active")


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            "id", "email", "name", "company_name", "company_website",
            "source", "profile_url", "persona", "status",
            "created_at", "updated_at",
        )
        read_only_fields = ("status", "created_at", "updated_at")