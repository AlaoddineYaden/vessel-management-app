# crew/apps.py
from django.apps import AppConfig


class CrewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crew'
    verbose_name = 'Vessel Crew Management'
    
    def ready(self):
        # Import signal handlers
        import crew.signals