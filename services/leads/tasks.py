from celery import shared_task
from django.utils import timezone
from .models import Lead


@shared_task
def research_lead(lead_id):
    try:
        lead = Lead.objects.get(pk=lead_id)
    except Lead.DoesNotExist:
        return
        
    lead.updated_at = timezone.now()
    lead.save(update_fields=["updated_at"])