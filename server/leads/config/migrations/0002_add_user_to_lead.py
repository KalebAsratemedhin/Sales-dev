from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    # No-op: `Lead.user` is already created in 0001_initial. This migration is
    # retained only to preserve the dependency graph for 0003/0004.
    dependencies = [
        ("config", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = []