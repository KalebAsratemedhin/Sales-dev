# Generated manually for LinkedIn sync metrics and follow-up status.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("config", "0002_add_user_to_lead"),
    ]

    operations = [
        migrations.AddField(
            model_name="lead",
            name="linkedin_comment_count",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Times scraper saw this lead in a post's comment section (existing leads only).",
            ),
        ),
        migrations.AlterField(
            model_name="lead",
            name="status",
            field=models.CharField(
                choices=[
                    ("new", "New"),
                    ("researched", "Researched"),
                    ("emailed", "Emailed"),
                    ("replied", "Replied"),
                    ("meeting_booked", "Meeting booked"),
                    ("follow_up_required", "Follow-up required"),
                ],
                db_index=True,
                default="new",
                max_length=32,
            ),
        ),
        migrations.CreateModel(
            name="LinkedInSyncedPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("post_url", models.URLField(db_index=True, max_length=2048, unique=True)),
                ("first_synced_at", models.DateTimeField(auto_now_add=True)),
                ("last_synced_at", models.DateTimeField(auto_now=True)),
                (
                    "synced_by_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="linkedin_synced_posts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-last_synced_at"]},
        ),
    ]
