from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.exceptions import ExpectedError, TransientError
from core.services.n8n_client import n8n_configured
from core.services.google_gmail_oauth import (
    build_authorize_url,
    connection_status,
    disconnect,
    exchange_code,
    oauth_app_configured,
    resync_n8n,
)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gmail_status(request):
    return Response(connection_status(request.user.id))


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gmail_auth_url(request):
    try:
        payload = build_authorize_url(request.user.id)
    except ExpectedError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(payload)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gmail_exchange(request):
    data = request.data or {}
    try:
        exchange_code(
            request.user.id,
            code=(data.get("code") or "").strip(),
            state=(data.get("state") or "").strip(),
        )
    except ExpectedError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except TransientError as e:
        return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(connection_status(request.user.id))


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gmail_disconnect(request):
    disconnect(request.user.id)
    return Response(
        {
            "connected": False,
            "oauth_app_configured": oauth_app_configured(),
            "n8n_configured": n8n_configured(),
        }
    )


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gmail_sync_n8n(request):
    try:
        result = resync_n8n(request.user.id)
    except ExpectedError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except TransientError as e:
        return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(result)
