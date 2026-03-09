from django.db import models

class Research(models.Model):
    lead = models.OneToOneField(
        "leads.Lead",
        on_delete=models.CASCADE,
        related_name="research",
    )
    website_summary = models.TextField(blank=True)
    pain_points = models.JSONField(default=list, help_text="List of pain point strings")
    use_cases = models.JSONField(default=list, help_text="List of use case strings")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Research for {self.lead.email}"