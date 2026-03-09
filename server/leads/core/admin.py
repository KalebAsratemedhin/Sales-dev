from django.contrib import admin
from core.models import Lead, Persona


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "company_name", "status", "source", "created_at")
    list_filter = ("status", "source")
    search_fields = ("email", "name", "company_name")