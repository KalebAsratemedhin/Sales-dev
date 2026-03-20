from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import AuthenticationFailed, TokenError
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                {"email": ["An account with this email already exists."]}
            )
        return value.lower().strip()

    def create_user(self, *, full_name: str, email: str, password: str) -> User:
        return User.objects.create_user(
            username=email,
            email=email,
            first_name=full_name.strip(),
            password=password,
        )


class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email", "").lower().strip()
        password = attrs.get("password", "")

        user = authenticate(username=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid email or password.")

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = attrs.get("refresh")
        try:
            token = RefreshToken(refresh)
        except TokenError:
            raise AuthenticationFailed("Invalid refresh token.")
        return {"access": str(token.access_token)}

