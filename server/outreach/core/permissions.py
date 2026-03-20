from django.conf import settings
from rest_framework.permissions import BasePermission


class InternalSecretOrAuthenticated(BasePermission):
    """
    Allows internal calls authenticated via X-Internal-Secret, otherwise requires JWT auth.
    """

    def has_permission(self, request, view) -> bool:
        secret = getattr(settings, "LEADS_SERVICE_INTERNAL_SECRET", "") or ""
        if secret and request.headers.get("X-Internal-Secret") == secret:
            return True
        return bool(getattr(request, "user", None) and request.user.is_authenticated)

