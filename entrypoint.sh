#!/bin/sh

python manage.py runserver localhost:8001 & python -m celery -A myassistant.celery:app worker