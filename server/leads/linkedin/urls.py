from django.urls import path

from linkedin.api import views
from linkedin.api import job_views

urlpatterns = [
    path("sync/posts/", views.sync_from_posts),
    path("sync/profile/", views.sync_from_profile),
    path("sync/profile/async/", job_views.start_profile_sync_job),
    path("sync/jobs/<int:job_id>/", job_views.get_sync_job),
]
