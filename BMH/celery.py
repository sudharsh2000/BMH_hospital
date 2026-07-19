import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE','BMH.settings' )
app=Celery('BMH')
app.config_from_object('django.conf:settings',namespace='CELERY')
app.autodiscover_tasks()