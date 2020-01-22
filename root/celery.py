from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')
from django.conf import settings
from root.settings import BROKER_URL, BACKEND_URL

app = Celery('tasks', broker=BROKER_URL, backend=BACKEND_URL)


# app.config_from_object('django.conf:settings', namespace='CELERY')

# app = Celery('root')
# app.config_from_object('django.conf:settings')



app.autodiscover_tasks(settings.INSTALLED_APPS)

# app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
