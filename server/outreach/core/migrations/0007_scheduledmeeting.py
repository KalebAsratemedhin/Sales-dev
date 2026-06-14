from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("outreach", "0006_emailthread_user_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScheduledMeeting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("lead_id", models.BigIntegerField(db_index=True)),
                ("google_event_id", models.CharField(blank=True, default="", max_length=255)),
                ("html_link", models.URLField(blank=True, default="")),
                ("title", models.CharField(blank=True, default="", max_length=255)),
                ("start_at", models.DateTimeField()),
                ("duration_minutes", models.PositiveIntegerField(default=30)),
                ("lead_email", models.EmailField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "thread",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="meetings",
                        to="outreach.emailthread",
                    ),
                ),
            ],
            options={
                "ordering": ["-start_at"],
            },
        ),
    ]
