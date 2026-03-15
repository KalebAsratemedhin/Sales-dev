from datetime import datetime

from rest_framework import serializers


class SyncFromPostsSerializer(serializers.Serializer):
    post_urls = serializers.ListField(
        child=serializers.CharField(allow_blank=False),
        allow_empty=False,
        help_text="Post URLs or activity IDs",
    )
    persona_id = serializers.IntegerField(required=False, allow_null=True)

    def to_internal_value(self, data):
        if data.get("post_urls") is not None and isinstance(data["post_urls"], str):
            data = {**data, "post_urls": [data["post_urls"]]}
        return super().to_internal_value(data)


class SyncFromProfileSerializer(serializers.Serializer):
    profile_url = serializers.URLField(allow_blank=False)
    start_date = serializers.CharField(allow_blank=False)
    end_date = serializers.CharField(allow_blank=False)
    persona_id = serializers.IntegerField(required=False, allow_null=True)
    max_scrolls = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100)

    def validate_profile_url(self, value):
        if "/in/" not in (value or ""):
            raise serializers.ValidationError("profile_url must be a LinkedIn profile (e.g. .../in/username/).")
        return (value or "").strip()

    def _parse_date(self, s):
        try:
            return datetime.strptime(str(s).strip()[:10], "%Y-%m-%d").date()
        except ValueError as e:
            raise serializers.ValidationError("Use YYYY-MM-DD.") from e

    def validate_start_date(self, value):
        return self._parse_date(value)

    def validate_end_date(self, value):
        return self._parse_date(value)

    def validate(self, attrs):
        if attrs["start_date"] > attrs["end_date"]:
            raise serializers.ValidationError({"end_date": "start_date must be <= end_date."})
        return attrs
