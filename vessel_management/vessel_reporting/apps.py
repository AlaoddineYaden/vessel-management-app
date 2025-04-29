from django.apps import AppConfig


class VesselReportingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vessel_reporting'
    
    def ready(self):
        # Import celery tasks to ensure they're registered
        from . import tasks 