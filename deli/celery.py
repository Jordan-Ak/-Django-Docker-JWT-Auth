import os

from django.conf import settings

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deli.settings')


app = Celery('deli', backend='rpc://')#, broker='pyamqp://')# added a result backend here to send results when needed
#This allows celery to return results from async method


# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')