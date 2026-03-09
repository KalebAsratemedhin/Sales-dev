from django.contrib import admin
from .models import Lead, Persona
from .tasks import research_lead


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "company_name", "status", "source", "created_at")
    list_filter = ("status", "source")
    search_fields = ("email", "name", "company_name")
    actions = ["enqueue_research"]

    @admin.action(description="Enqueue research for selected leads")
    def enqueue_research(self, request, queryset):
        for lead in queryset:
            research_lead.delay(lead.id)
        self.message_user(request, f"Enqueued research for {queryset.count()} lead(s).")