import os
import django
from core.messaging import run_consumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
run_consumer()