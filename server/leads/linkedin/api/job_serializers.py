from rest_framework import serializers


class StartProfileSyncJobSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    max_scrolls = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100)

    def validate(self, attrs):
        if attrs["start_date"] > attrs["end_date"]:
            raise serializers.ValidationError({"end_date": "start_date must be <= end_date."})
        return attrs

