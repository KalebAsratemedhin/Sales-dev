from django.db import migrations, models


def merge_google_connections(apps, schema_editor):
    GoogleConnection = apps.get_model("outreach", "GoogleConnection")
    GmailConnection = apps.get_model("outreach", "GmailConnection")
    GoogleCalendarConnection = apps.get_model("outreach", "GoogleCalendarConnection")

    user_ids = set(GmailConnection.objects.values_list("user_id", flat=True)) | set(
        GoogleCalendarConnection.objects.values_list("user_id", flat=True)
    )

    for user_id in user_ids:
        gmail = GmailConnection.objects.filter(user_id=user_id).first()
        cal = GoogleCalendarConnection.objects.filter(user_id=user_id).first()
        token_src = gmail or cal
        if not token_src:
            continue

        GoogleConnection.objects.update_or_create(
            user_id=user_id,
            defaults={
                "refresh_token": token_src.refresh_token or "",
                "access_token": token_src.access_token or "",
                "expires_at": token_src.expires_at,
                "scope": token_src.scope or "",
                "google_email": (gmail.google_email if gmail else "") or (cal.google_email if cal else ""),
                "oauth_state": "",
                "calendar_id": (cal.calendar_id if cal else "") or "primary",
                "timezone": cal.timezone if cal else "",
                "meeting_duration_minutes": cal.meeting_duration_minutes if cal else None,
                "n8n_credential_id": gmail.n8n_credential_id if gmail else "",
                "n8n_workflow_id": gmail.n8n_workflow_id if gmail else "",
                "n8n_sync_error": gmail.n8n_sync_error if gmail else "",
                "n8n_synced_at": gmail.n8n_synced_at if gmail else None,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("outreach", "0009_gmail_connection"),
    ]

    operations = [
        migrations.CreateModel(
            name="GoogleConnection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.BigIntegerField(db_index=True, unique=True)),
                ("refresh_token", models.TextField(blank=True, default="")),
                ("access_token", models.TextField(blank=True, default="")),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("scope", models.TextField(blank=True, default="")),
                ("google_email", models.EmailField(blank=True, default="")),
                ("oauth_state", models.CharField(blank=True, default="", max_length=64)),
                ("calendar_id", models.CharField(blank=True, default="primary", max_length=255)),
                ("timezone", models.CharField(blank=True, default="", max_length=64)),
                ("meeting_duration_minutes", models.PositiveIntegerField(blank=True, null=True)),
                ("n8n_credential_id", models.CharField(blank=True, default="", max_length=64)),
                ("n8n_workflow_id", models.CharField(blank=True, default="", max_length=64)),
                ("n8n_sync_error", models.TextField(blank=True, default="")),
                ("n8n_synced_at", models.DateTimeField(blank=True, null=True)),
                ("connected_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RunPython(merge_google_connections, migrations.RunPython.noop),
        migrations.DeleteModel(name="GmailConnection"),
        migrations.DeleteModel(name="GoogleCalendarConnection"),
    ]
