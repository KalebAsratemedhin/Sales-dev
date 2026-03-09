#!/bin/bash
set -e
python manage.py migrate --noinput
python core/run_consumer.py &
exec "$@"