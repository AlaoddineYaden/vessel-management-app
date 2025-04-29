from django.apps import AppConfig


class SafetyProceduresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'safety_procedures'
    verbose_name = 'Safety Procedures & ISM Manuals'

    def ready(self):
        import safety_procedures.signals  # noqa
