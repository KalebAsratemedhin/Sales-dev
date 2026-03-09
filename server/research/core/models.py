from django.db import models


class Research(models.Model):
    lead_id = models.BigIntegerField(unique=True, db_index=True)
    website_summary = models.TextField(blank=True)
    pain_points = models.JSONField(default=list)
    use_cases = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Research for lead_id={self.lead_id}"