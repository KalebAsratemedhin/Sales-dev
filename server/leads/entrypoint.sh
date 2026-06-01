#!/bin/bash
set -e
for i in 1 2 3 4 5; do
  python manage.py migrate --noinput && break
  echo "migrate attempt $i failed; retrying in 3s"; sleep 3
done
celery -A config worker -Q leads -l info --concurrency=2 &
exec "$@"
