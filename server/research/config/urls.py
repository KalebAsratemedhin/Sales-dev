from django.contrib import admin
from django.urls import path

from core.api import research_by_lead, research_list, research_stats

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/research/stats/", research_stats),
    path("api/research/", research_list),
    path("api/research/leads/<int:lead_id>/", research_by_lead),
]