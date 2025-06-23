import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE','message_service.settings')

app = Celery('message_service') #name for the celery worker
app.config_from_object('django.conf:settings',namespace='CELERY')# tell the app to look for settings that start with CELERY
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'cleanup_one_to_one_messages_every_hour':{
        'task': 'message.tasks.cleanup_one_to_one_messages',
        'schedule':crontab(minute='*/60')
    },

    'cleanup_group_messages_every_hour': {
        'task': 'message.tasks.cleanup_group_messages',  # Fully qualified task name
        'schedule': crontab(minute='*/60'),  # Run every 1 minute
    },
}

#tasks defined inside the `message/tasks.py` file.