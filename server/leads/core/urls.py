from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core import views
from core.webhooks import linkedin_lead_sync_webhook

router = DefaultRouter()
router.register("", views.LeadViewSet, basename="lead")
urlpatterns = [
    path("webhooks/linkedin/lead-sync/", linkedin_lead_sync_webhook, name="linkedin-lead-sync-webhook"),
    path("", include(router.urls)),
]