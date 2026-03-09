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

    email = models.EmailField()
    name = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    company_website = models.URLField(blank=True)
    source = models.CharField(max_length=32, choices=Source.choices, default=Source.CSV)
    profile_url = models.URLField(blank=True)
    persona = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.NEW, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email or self.name or str(self.pk)