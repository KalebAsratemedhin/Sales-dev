from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="emailthread",
            name="company_name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="emailthread",
            name="research_summary",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="emailthread",
            name="pain_points",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="emailthread",
            name="use_cases",
            field=models.JSONField(default=list),
        ),
    ]

