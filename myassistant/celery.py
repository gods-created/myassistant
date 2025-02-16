from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myassistant.settings')

app = Celery('celery_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.task_queues = {
    'high_priority': {
        'routing_key': 'high_priority'
    },
    'low_priority': {
        'routing_key': 'low_priority'
    }
}
app.autodiscover_tasks()