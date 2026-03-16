from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_emailthread_research_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="OutreachConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("linkedin_url", models.CharField(blank=True, max_length=512)),
                ("calendly_scheduling_url", models.CharField(blank=True, max_length=512)),
                ("product_docs_path", models.CharField(blank=True, max_length=512)),
                ("chroma_collection_name", models.CharField(blank=True, default="product_docs", max_length=128)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Outreach config",
                "verbose_name_plural": "Outreach config",
            },
        ),
    ]
