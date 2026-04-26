from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("config", "0003_lead_comments_synced_posts_followup_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="LinkedInLeadSyncConnection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("access_token", models.TextField(blank=True, default="")),
                ("refresh_token", models.TextField(blank=True, default="")),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("scope", models.TextField(blank=True, default="")),
                ("token_type", models.CharField(blank=True, default="Bearer", max_length=32)),
                ("organization_urn", models.CharField(blank=True, default="", max_length=128)),
                ("sponsored_account_urn", models.CharField(blank=True, default="", max_length=128)),
                ("last_synced_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="linkedin_lead_sync_connection",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LinkedInLeadGenResponseCursor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("response_urn", models.CharField(db_index=True, max_length=255, unique=True)),
                ("received_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="linkedin_leadgen_responses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-received_at"]},
        ),
    ]

