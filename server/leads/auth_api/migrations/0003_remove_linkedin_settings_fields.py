from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("auth_api", "0002_outreachsettings_linkedin_last_sync"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="outreachsettings",
            name="linkedin_last_sync",
        ),
        migrations.RemoveField(
            model_name="outreachsettings",
            name="linkedin_profile_url",
        ),
    ]
