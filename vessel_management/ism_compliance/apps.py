from django.apps import AppConfig


class ISMComplianceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ism_compliance'
    verbose_name = 'ISM Compliance Checklists'
    
    def ready(self):
        """Perform initialization tasks when the app is ready"""
        pass  # You can add any startup tasks here

