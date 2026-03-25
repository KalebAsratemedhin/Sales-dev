import logging

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from auth_api.models import OutreachSettings
from core.permissions import InternalSecretOrAuthenticated
from linkedin.api.job_serializers import StartProfileSyncJobSerializer
from linkedin.jobs.messaging import publish_linkedin_sync_profile
from linkedin.models import LinkedInSyncJob

logger = logging.getLogger(__name__)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([InternalSecretOrAuthenticated])
def start_profile_sync_job(request):
    serializer = StartProfileSyncJobSerializer(data=request.data or {})
    if not serializer.is_valid():
        return Response(
            {"error": "Validation failed.", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not getattr(request.user, "is_authenticated", False):
        return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

    settings_obj, _ = OutreachSettings.objects.get_or_create(user=request.user)
    profile_url = (settings_obj.linkedin_profile_url or "").strip()
    if not profile_url:
        return Response(
            {"error": "LinkedIn profile URL not set. Update it in Settings first."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = serializer.validated_data
    job = LinkedInSyncJob.objects.create(
        user=request.user,
        profile_url=profile_url,
        start_date=data["start_date"],
        end_date=data["end_date"],
        max_scrolls=data.get("max_scrolls", 10),
        status=LinkedInSyncJob.Status.QUEUED,
    )
    publish_linkedin_sync_profile({"job_id": job.id, "user_id": request.user.id})
    return Response({"job_id": job.id}, status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([InternalSecretOrAuthenticated])
def get_sync_job(request, job_id: int):
    if not getattr(request.user, "is_authenticated", False):
        return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

    job = LinkedInSyncJob.objects.filter(id=job_id, user=request.user).first()
    if not job:
        return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response(
        {
            "id": job.id,
            "status": job.status,
            "created": job.created,
            "updated": job.updated,
            "error": job.error,
            "start_date": job.start_date.isoformat(),
            "end_date": job.end_date.isoformat(),
            "updated_at": job.updated_at.isoformat(),
        },
        status=status.HTTP_200_OK,
    )

