from __future__ import annotations

import os

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.services.linkedin_lead_sync_service import LinkedInLeadSyncService


@api_view(["POST"])
@permission_classes([AllowAny])
def linkedin_lead_sync_webhook(request):
    expected = (os.environ.get("LINKEDIN_WEBHOOK_SECRET") or "").strip()
    if expected:
        got = (request.headers.get("X-LinkedIn-Webhook-Secret") or "").strip()
        if got != expected:
            return Response({"error": "invalid webhook secret"}, status=status.HTTP_403_FORBIDDEN)

    payload = request.data or {}
    user_id = payload.get("user_id")
    owner = payload.get("owner") or {}
    if isinstance(user_id, int) and isinstance(owner, dict) and owner:
        try:
            svc = LinkedInLeadSyncService()
            svc.pull_and_import(user_id=user_id, owner=owner, start=0, count=50)
        except Exception:
            pass

    return Response({"ok": True}, status=status.HTTP_200_OK)

