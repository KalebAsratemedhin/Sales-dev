import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from linkedin.api.serializers import SyncFromPostsSerializer, SyncFromProfileSerializer
from linkedin.sync import sync_leads_from_posts, sync_leads_from_profile

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([AllowAny])
def sync_from_posts(request):
    serializer = SyncFromPostsSerializer(data=request.data or {})
    if not serializer.is_valid():
        return Response(
            {"error": "Validation failed.", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    data = serializer.validated_data
    try:
        created, updated = sync_leads_from_posts(
            data["post_urls"],
            persona_id=data.get("persona_id"),
        )
        return Response({"created": created, "updated": updated}, status=status.HTTP_200_OK)
    except RuntimeError as e:
        logger.warning("Sync from posts RuntimeError: %s", e)
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as e:
        logger.exception("Sync from posts failed: %s", e)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([AllowAny])
def sync_from_profile(request):
    serializer = SyncFromProfileSerializer(data=request.data or {})
    if not serializer.is_valid():
        return Response(
            {"error": "Validation failed.", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    data = serializer.validated_data
    try:
        created, updated = sync_leads_from_profile(
            data["profile_url"],
            data["start_date"],
            data["end_date"],
            persona_id=data.get("persona_id"),
            max_activity_scrolls=data.get("max_scrolls", 10),
        )
        return Response({"created": created, "updated": updated}, status=status.HTTP_200_OK)
    except RuntimeError as e:
        logger.warning("Sync from profile RuntimeError: %s", e)
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as e:
        logger.exception("Sync from profile failed: %s", e)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
