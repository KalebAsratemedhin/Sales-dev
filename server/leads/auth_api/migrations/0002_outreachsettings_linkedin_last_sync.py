from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth_api", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="outreachsettings",
            name="linkedin_last_sync",
            field=models.DateField(blank=True, null=True),
        ),
    ]

