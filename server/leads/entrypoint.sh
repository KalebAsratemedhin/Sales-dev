#!/bin/bash
set -e
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python -m core.run_consumer &
exec "$@"