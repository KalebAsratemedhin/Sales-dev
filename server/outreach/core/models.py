from django.db import models


class EmailThread(models.Model):
    lead_id = models.BigIntegerField(db_index=True)
    user_id = models.BigIntegerField(db_index=True, default=0)
    to_email = models.EmailField(blank=True, default="")
    name = models.CharField(max_length=255, blank=True, default="")
    gmail_thread_id = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=512, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    research_summary = models.TextField(blank=True, default="")
    pain_points = models.JSONField(default=list)
    use_cases = models.JSONField(default=list)
    last_message_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EmailThread lead_id={self.lead_id}"


class SentEmail(models.Model):
    class Direction(models.TextChoices):
        OUTBOUND = "outbound", "Outbound"
        INBOUND = "inbound", "Inbound"

    thread = models.ForeignKey(EmailThread, on_delete=models.CASCADE, related_name="emails")
    message_id = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    direction = models.CharField(max_length=16, choices=Direction.choices)
    body = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.direction} {self.message_id}"


class OutreachConfig(models.Model):
    linkedin_url = models.CharField(max_length=512, blank=True)
    calendly_scheduling_url = models.CharField(max_length=512, blank=True)
    product_docs_path = models.CharField(max_length=512, blank=True)
    chroma_collection_name = models.CharField(max_length=128, blank=True, default="product_docs")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Outreach config"
        verbose_name_plural = "Outreach config"

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ScheduledMeeting(models.Model):
    thread = models.ForeignKey(EmailThread, on_delete=models.CASCADE, related_name="meetings")
    lead_id = models.BigIntegerField(db_index=True)
    google_event_id = models.CharField(max_length=255, blank=True, default="")
    html_link = models.URLField(blank=True, default="")
    title = models.CharField(max_length=255, blank=True, default="")
    start_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    lead_email = models.EmailField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_at"]

    def __str__(self):
        return f"ScheduledMeeting lead_id={self.lead_id} start={self.start_at}"