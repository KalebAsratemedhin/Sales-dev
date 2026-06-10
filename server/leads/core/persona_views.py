from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Persona
from core.permissions import InternalSecretOrAuthenticated
from core.serializers import PersonaSerializer


class PersonaViewSet(viewsets.ModelViewSet):
    queryset = Persona.objects.all().order_by("name")
    serializer_class = PersonaSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [InternalSecretOrAuthenticated]
