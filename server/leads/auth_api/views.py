from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from auth_api.serializers import (
    EmailLoginSerializer,
    RegisterSerializer,
    RefreshSerializer,
)


class EmailRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)

        user = serializer.create_user(
            full_name=serializer.validated_data["full_name"],
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        # Return JWT immediately after registration.
        refresh = RefreshToken.for_user(user)
        return Response(
            {"access": str(refresh.access_token), "refresh": str(refresh)},
            status=status.HTTP_201_CREATED,
        )


class EmailLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailLoginSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class MeView(APIView):
    """Return the authenticated user's display info for the frontend header."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                # `RegisterSerializer` stores full name in `first_name`.
                "full_name": getattr(user, "first_name", "") or "",
                "email": getattr(user, "email", "") or "",
            },
            status=status.HTTP_200_OK,
        )

