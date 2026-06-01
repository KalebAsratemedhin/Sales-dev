from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("outreach", "0003_outreachconfig"),
    ]

    operations = [
        migrations.AddField(
            model_name="sentemail",
            name="body",
            field=models.TextField(blank=True, default=""),
        ),
    ]

