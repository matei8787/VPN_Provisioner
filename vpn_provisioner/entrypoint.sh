#!/bin/bash
set -e

python manage.py collectstatic --no-inpuit
python manage.py makemigrations --no-input
python manage.py migrate --no-input

exec "$@"