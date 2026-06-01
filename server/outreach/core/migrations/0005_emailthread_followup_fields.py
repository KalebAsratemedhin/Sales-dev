from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("outreach", "0004_sentemail_body"),
    ]

    operations = [
        migrations.AddField(
            model_name="emailthread",
            name="to_email",
            field=models.EmailField(blank=True, default="", max_length=254),
        ),
        migrations.AddField(
            model_name="emailthread",
            name="name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
