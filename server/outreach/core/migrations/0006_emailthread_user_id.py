from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("outreach", "0005_emailthread_followup_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="emailthread",
            name="user_id",
            field=models.BigIntegerField(db_index=True, default=0),
        ),
    ]
