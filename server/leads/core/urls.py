from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views
from core.persona_views import PersonaViewSet
router = DefaultRouter()
router.register("personas", PersonaViewSet, basename="persona")
router.register("", views.LeadViewSet, basename="lead")
urlpatterns = [
    path("", include(router.urls)),
]