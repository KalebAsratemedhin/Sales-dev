#!/bin/bash
set -e
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python core/run_consumer.py &
exec "$@"