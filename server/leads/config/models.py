from django.conf import settings
from django.db import models


class Persona(models.Model):
    name = models.CharField(max_length=255)
    title_keywords = models.TextField(blank=True)
    industry_keywords = models.TextField(blank=True)
    search_keywords = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Lead(models.Model):
    class Source(models.TextChoices):
        LINKEDIN = "linkedin", "LinkedIn"
        TWITTER = "twitter", "Twitter"
        CSV = "csv", "CSV"

    class Status(models.TextChoices):
        NEW = "new", "New"
        RESEARCHED = "researched", "Researched"
        EMAILED = "emailed", "Emailed"
        REPLIED = "replied", "Replied"
        MEETING_BOOKED = "meeting_booked", "Meeting booked"
        FOLLOW_UP_REQUIRED = "follow_up_required", "Follow-up required"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leads",
        null=True,
        blank=True,
        db_index=True,
    )

    email = models.EmailField()
    name = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    company_website = models.URLField(blank=True)
    source = models.CharField(max_length=32, choices=Source.choices, default=Source.CSV)
    profile_url = models.URLField(blank=True)
    persona = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.NEW, db_index=True)
    linkedin_comment_count = models.PositiveIntegerField(
        default=0,
        help_text="Times scraper saw this lead in a post's comment section (existing leads only).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email or self.name or str(self.pk)


class LinkedInSyncedPost(models.Model):
    """Canonical LinkedIn post URLs the scraper has processed (deduped)."""

    post_url = models.URLField(max_length=2048, unique=True, db_index=True)
    synced_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linkedin_synced_posts",
    )
    first_synced_at = models.DateTimeField(auto_now_add=True)
    last_synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_synced_at"]

    def __str__(self):
        return self.post_url[:80]