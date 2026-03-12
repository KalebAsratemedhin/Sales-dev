from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/leads/", include("core.urls")),
    path("api/linkedin/", include("linkedin.urls")),
]