from django.db import models


class Persona(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Lead(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=64, default="new")
    source = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class EmailThread(models.Model):
    lead_id = models.BigIntegerField(db_index=True)
    user_id = models.BigIntegerField(db_index=True, default=0)
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