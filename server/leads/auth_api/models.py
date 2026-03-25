from __future__ import annotations

import os
from django.conf import settings
from django.db import models
from django.utils.text import get_valid_filename


def profile_pic_upload_to(instance: "UserProfile", filename: str) -> str:
    safe = get_valid_filename(os.path.basename(filename)) or "profile_pic"
    return f"profile_pics/{instance.user_id}/{safe}"


def product_doc_upload_to(instance: "ProductDoc", filename: str) -> str:
    safe = get_valid_filename(os.path.basename(filename)) or "document"
    return f"product_docs/{instance.user_id}/{safe}"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    profile_pic = models.FileField(upload_to=profile_pic_upload_to, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"UserProfile user_id={self.user_id}"


class OutreachSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="outreach_settings")
    linkedin_profile_url = models.CharField(max_length=512, blank=True)
    calendly_scheduling_url = models.CharField(max_length=512, blank=True)
    linkedin_last_sync = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"OutreachSettings user_id={self.user_id}"


class ProductDoc(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="product_docs")
    file = models.FileField(upload_to=product_doc_upload_to)
    original_filename = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"ProductDoc id={self.id} user_id={self.user_id}"

