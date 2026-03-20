from django.urls import path

from auth_api.views import EmailLoginView, EmailRegisterView, MeView, RefreshView

from auth_api.user_settings_views import (
    ProductDocFileView,
    ProductDocsView,
    ProfilePicView,
    ProfileView,
    OutreachSettingsView,
)

urlpatterns = [
    path("register/", EmailRegisterView.as_view(), name="auth-register"),
    path("login/", EmailLoginView.as_view(), name="auth-login"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),

    path("profile/", ProfileView.as_view(), name="auth-profile"),
    path("profile/pic/", ProfilePicView.as_view(), name="auth-profile-pic"),
    path("settings/", OutreachSettingsView.as_view(), name="auth-settings"),
    path("product-docs/", ProductDocsView.as_view(), name="auth-product-docs"),
    path("product-docs/<int:doc_id>/", ProductDocFileView.as_view(), name="auth-product-doc-file"),
]

