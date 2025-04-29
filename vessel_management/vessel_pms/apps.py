from django.apps import AppConfig


class VesselPmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vessel_pms'
    verbose_name = 'Vessel Maintenance Management'

    def ready(self):
        import vessel_pms.signals