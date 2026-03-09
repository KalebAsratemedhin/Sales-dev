from django.contrib import admin
from core.models import Research


@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    list_display = ("lead_id", "website_summary_preview", "created_at")

    def website_summary_preview(self, obj):
        s = obj.website_summary or ""
        return (s[:80] + "...") if len(s) > 80 else s
    
    website_summary_preview.short_description = "Summary"