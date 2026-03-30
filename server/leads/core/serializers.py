from rest_framework import serializers
from core.models import Lead


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            "id", "email", "name", "company_name", "company_website",
            "source", "profile_url", "persona", "status", "linkedin_comment_count",
            "created_at", "updated_at",
        )
        read_only_fields = ("status", "linkedin_comment_count", "created_at", "updated_at")