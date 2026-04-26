from django.contrib.auth import get_user_model
from django.test import TestCase

from config.models import Lead
from core.services.linkedin_csv_import_service import LinkedInConnectionsCsvImportService


User = get_user_model()


class LinkedInConnectionsCsvImportServiceTests(TestCase):
    def test_import_creates_leads_and_placeholders(self):
        user = User.objects.create_user(username="t", email="t@example.com", password="pw")

        csv_bytes = (
            "First Name,Last Name,Email Address,Company,Position,Connected On\n"
            "Ada,Lovelace,ada@example.com,Analytical Engines,CTO,2026-01-01\n"
            "Grace,Hopper,,Navy,Admiral,2026-01-02\n"
        ).encode("utf-8")

        svc = LinkedInConnectionsCsvImportService()
        result = svc.import_file(user_id=user.id, file_bytes=csv_bytes)

        self.assertEqual(result.created, 2)
        self.assertEqual(Lead.objects.filter(user=user, source=Lead.Source.LINKEDIN).count(), 2)
        self.assertTrue(Lead.objects.filter(email="ada@example.com").exists())
        self.assertTrue(
            Lead.objects.filter(email__endswith="@linkedin-export.placeholder", name__icontains="Grace").exists()
        )
