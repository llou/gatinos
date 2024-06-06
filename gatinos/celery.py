import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gatinos.settings')

app = Celery('gatinos', broker='redis://redis', backend='redis://redis')
app.config_from_object('django.conf:settings', namespace="CELERY")
app.autodiscover_tasks()
