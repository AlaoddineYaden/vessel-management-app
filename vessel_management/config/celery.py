import os
import platform
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the Celery app
app = Celery('vessel_management')

# Use the Django settings for Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configure Celery for Windows
if platform.system().lower() == 'windows':
    app.conf.update(
        worker_pool_restarts=True,
        worker_pool='threads',
        worker_concurrency=4,
    )

# Load tasks modules from all registered Django app configs
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'update-overdue-tasks': {
        'task': 'vessel_pms.tasks.update_overdue_tasks',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
    'generate-recurring-tasks': {
        'task': 'vessel_pms.tasks.generate_recurring_tasks',
        'schedule': crontab(hour=0, minute=15),  # Run daily at 00:15
    },
}