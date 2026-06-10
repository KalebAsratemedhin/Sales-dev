from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("config", "0006_alter_lead_id_alter_linkedinleadgenresponsecursor_id_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="lead",
            name="linkedin_comment_count",
        ),
        migrations.DeleteModel(
            name="LinkedInLeadGenResponseCursor",
        ),
        migrations.DeleteModel(
            name="LinkedInLeadSyncConnection",
        ),
        migrations.DeleteModel(
            name="LinkedInSyncedPost",
        ),
    ]
