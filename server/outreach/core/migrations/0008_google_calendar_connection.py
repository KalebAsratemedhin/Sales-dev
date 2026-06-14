from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("outreach", "0007_scheduledmeeting"),
    ]

    operations = [
        migrations.AddField(
            model_name="outreachconfig",
            name="default_timezone",
            field=models.CharField(blank=True, default="UTC", max_length=64),
        ),
        migrations.AddField(
            model_name="outreachconfig",
            name="default_meeting_duration_minutes",
            field=models.PositiveIntegerField(default=30),
        ),
        migrations.CreateModel(
            name="GoogleCalendarConnection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.BigIntegerField(db_index=True, unique=True)),
                ("refresh_token", models.TextField(blank=True, default="")),
                ("access_token", models.TextField(blank=True, default="")),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("scope", models.TextField(blank=True, default="")),
                ("google_email", models.EmailField(blank=True, default="")),
                ("calendar_id", models.CharField(blank=True, default="primary", max_length=255)),
                ("timezone", models.CharField(blank=True, default="", max_length=64)),
                ("meeting_duration_minutes", models.PositiveIntegerField(blank=True, null=True)),
                ("oauth_state", models.CharField(blank=True, default="", max_length=64)),
                ("connected_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
