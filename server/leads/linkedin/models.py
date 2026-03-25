from __future__ import annotations

from django.conf import settings
from django.db import models


class LinkedInSyncJob(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="linkedin_sync_jobs",
    )

    profile_url = models.CharField(max_length=512)
    start_date = models.DateField()
    end_date = models.DateField()
    max_scrolls = models.IntegerField(default=10)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED, db_index=True)
    created = models.IntegerField(default=0)
    updated = models.IntegerField(default=0)
    error = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"LinkedInSyncJob id={self.id} user_id={self.user_id} status={self.status}"

