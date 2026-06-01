from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("research", "0002_research_raw_content_preview"),
    ]

    operations = [
        migrations.AlterField(
            model_name="research",
            name="raw_content_preview",
            field=models.TextField(blank=True),
        ),
    ]
