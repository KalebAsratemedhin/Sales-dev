from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("outreach", "0008_google_calendar_connection"),
    ]

    operations = [
        migrations.CreateModel(
            name="GmailConnection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.BigIntegerField(db_index=True, unique=True)),
                ("refresh_token", models.TextField(blank=True, default="")),
                ("access_token", models.TextField(blank=True, default="")),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("scope", models.TextField(blank=True, default="")),
                ("google_email", models.EmailField(blank=True, default="")),
                ("oauth_state", models.CharField(blank=True, default="", max_length=64)),
                ("n8n_credential_id", models.CharField(blank=True, default="", max_length=64)),
                ("n8n_workflow_id", models.CharField(blank=True, default="", max_length=64)),
                ("n8n_sync_error", models.TextField(blank=True, default="")),
                ("n8n_synced_at", models.DateTimeField(blank=True, null=True)),
                ("connected_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
