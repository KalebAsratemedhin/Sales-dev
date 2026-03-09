import os
from core.messaging import run_consumer
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

run_consumer()