import logging
import os
from typing import Any

import requests
from django.contrib.auth import get_user_model
from django.http import FileResponse
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.permissions import InternalSecretOrAuthenticated

from .models import OutreachSettings, ProductDoc, UserProfile

logger = logging.getLogger("auth_api")
User = get_user_model()


def _get_target_user(request: Any) -> Any:
    if getattr(request, "user", None) is not None and getattr(request.user, "is_authenticated", False):
        return request.user

    user_id = (
        getattr(request, "query_params", {}).get("user_id")
        or getattr(request, "data", {}).get("user_id")
        or getattr(request, "GET", {}).get("user_id")
    )
    if user_id is None:
        return None
    return User.objects.filter(pk=user_id).first()


class ProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [InternalSecretOrAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        user = _get_target_user(request)
        if user is None:
            return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile_pic_url = "/api/auth/profile/pic/" if profile.profile_pic else None
        return Response(
            {
                "full_name": getattr(user, "first_name", "") or "",
                "email": getattr(user, "email", "") or "",
                "profile_pic_url": profile_pic_url,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        user = _get_target_user(request)
        if user is None:
            return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        full_name = request.data.get("full_name")
        if full_name is not None:
            user.first_name = str(full_name).strip()
            user.save(update_fields=["first_name"])

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if "profile_pic" in request.FILES:
            profile.profile_pic = request.FILES["profile_pic"]
            profile.save(update_fields=["profile_pic", "updated_at"])

        return self.get(request)


class ProfilePicView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [InternalSecretOrAuthenticated]

    def get(self, request):
        user = _get_target_user(request)
        if user is None:
            return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        profile = UserProfile.objects.filter(user=user).first()
        if not profile or not profile.profile_pic:
            return Response({"detail": "No profile picture uploaded."}, status=status.HTTP_404_NOT_FOUND)

        file_handle = profile.profile_pic.open("rb")
        return FileResponse(
            file_handle,
            as_attachment=False,
            filename=os.path.basename(profile.profile_pic.name),
        )


class OutreachSettingsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [InternalSecretOrAuthenticated]

    def get(self, request):
        user = _get_target_user(request)
        if user is None:
            return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        settings_obj, _ = OutreachSettings.objects.get_or_create(user=user)
        return Response(
            {
                "linkedin_profile_url": settings_obj.linkedin_profile_url or "",
                "calendly_scheduling_url": settings_obj.calendly_scheduling_url or "",
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        user = _get_target_user(request)
        if user is None:
            return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        settings_obj, _ = OutreachSettings.objects.get_or_create(user=user)
        linkedin_profile_url = request.data.get("linkedin_profile_url")
        calendly_scheduling_url = request.data.get("calendly_scheduling_url")

        if linkedin_profile_url is not None:
            settings_obj.linkedin_profile_url = str(linkedin_profile_url).strip()
        if calendly_scheduling_url is not None:
            settings_obj.calendly_scheduling_url = str(calendly_scheduling_url).strip()

        settings_obj.save(update_fields=["linkedin_profile_url", "calendly_scheduling_url", "updated_at"])
        return self.get(request)


class ProductDocsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [InternalSecretOrAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        user = _get_target_user(request)
        if user is None:
            return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        items = []
        for doc in ProductDoc.objects.filter(user=user).order_by("-uploaded_at")[:200]:
            items.append(
                {
                    "id": doc.id,
                    "filename": doc.original_filename or os.path.basename(doc.file.name),
                    "uploaded_at": doc.uploaded_at.isoformat(),
                }
            )

        return Response({"items": items}, status=status.HTTP_200_OK)

    def post(self, request):
        user = _get_target_user(request)
        if user is None:
            return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        files = request.FILES.getlist("files")
        if not files and "file" in request.FILES:
            files = [request.FILES["file"]]

        if not files:
            return Response({"detail": "No files provided. Use `files` multipart field."}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_docs: list[dict[str, Any]] = []
        for f in files[:50]:
            product = ProductDoc.objects.create(
                user=user,
                file=f,
                original_filename=str(getattr(f, "name", "") or "")[:255] or os.path.basename(str(f)),
            )
            uploaded_docs.append(
                {
                    "id": product.id,
                    "filename": product.original_filename or os.path.basename(product.file.name),
                }
            )

        internal_secret = os.environ.get("LEADS_SERVICE_INTERNAL_SECRET") or ""
        outreach_base_url = os.environ.get("OUTREACH_SERVICE_URL") or "http://outreach:8000"
        if internal_secret:
            try:
                r = requests.post(
                    f"{outreach_base_url}/api/outreach/ingest-docs/",
                    headers={"X-Internal-Secret": internal_secret},
                    json={"user_id": user.id},
                    timeout=60,
                )
                if r.status_code >= 400:
                    logger.warning("Ingest docs failed: status=%s body=%s", r.status_code, r.text[:500])
            except Exception:
                logger.exception("Ingest docs HTTP call failed")

        return Response({"uploaded": uploaded_docs}, status=status.HTTP_201_CREATED)


class ProductDocFileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [InternalSecretOrAuthenticated]

    def get(self, request, doc_id: int):
        user = _get_target_user(request)
        if user is None:
            return Response({"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        doc = ProductDoc.objects.filter(user=user, id=doc_id).first()
        if not doc or not doc.file:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        file_handle = doc.file.open("rb")
        filename = doc.original_filename or os.path.basename(doc.file.name)
        return FileResponse(file_handle, as_attachment=False, filename=filename)

