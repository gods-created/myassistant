celery:
	python -m celery -A myassistant.celery:app worker --concurrency=1

app:
	python manage.py runserver