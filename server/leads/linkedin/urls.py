from django.urls import path

from linkedin.api import views

urlpatterns = [
    path("sync/posts/", views.sync_from_posts),
    path("sync/profile/", views.sync_from_profile),
]
