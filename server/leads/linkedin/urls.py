from django.urls import path
from linkedin import views

urlpatterns = [
    path("sync/", views.sync),
]
