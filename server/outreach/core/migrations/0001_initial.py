from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="EmailThread",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("lead_id", models.BigIntegerField(db_index=True)),
                ("gmail_thread_id", models.CharField(blank=True, max_length=255)),
                ("subject", models.CharField(blank=True, max_length=512)),
                ("last_message_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="SentEmail",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message_id", models.CharField(max_length=255)),
                ("sent_at", models.DateTimeField(auto_now_add=True)),
                (
                    "direction",
                    models.CharField(
                        choices=[("outbound", "Outbound"), ("inbound", "Inbound")],
                        max_length=16,
                    ),
                ),
                (
                    "thread",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="emails",
                        to="outreach.EmailThread",
                    ),
                ),
            ],
        ),
    ]

