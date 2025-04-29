# 8. core/models.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='%(class)s_created',
        null=True, blank=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='%(class)s_updated',
        null=True, blank=True
    )
    
    class Meta:
        abstract = True

class Vessel(BaseModel):
    name = models.CharField(max_length=255)
    imo_number = models.CharField(max_length=20, unique=True)
    mmsi_number = models.CharField(max_length=20, blank=True, null=True)
    call_sign = models.CharField(max_length=20, blank=True, null=True)
    vessel_type = models.CharField(max_length=100)
    flag = models.CharField(max_length=100)
    build_year = models.PositiveIntegerField()
    length_overall = models.DecimalField(max_digits=10, decimal_places=2)
    beam = models.DecimalField(max_digits=10, decimal_places=2)
    draft = models.DecimalField(max_digits=10, decimal_places=2)
    gross_tonnage = models.DecimalField(max_digits=10, decimal_places=2)
    net_tonnage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} (IMO: {self.imo_number})"

class SystemLog(BaseModel):
    class LogLevel(models.TextChoices):
        INFO = 'INFO', _('Info')
        WARNING = 'WARNING', _('Warning')
        ERROR = 'ERROR', _('Error')
        CRITICAL = 'CRITICAL', _('Critical')
    
    level = models.CharField(max_length=10, choices=LogLevel.choices, default=LogLevel.INFO)
    message = models.TextField()
    source = models.CharField(max_length=255)  # Module or component that generated the log
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='log_entries',
        null=True, blank=True
    )
    
    def __str__(self):
        return f"{self.level} - {self.source} - {self.created_at}"

class File(BaseModel):
    file = models.FileField(upload_to='documents/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_size = models.PositiveIntegerField()  # Size in bytes
    content_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # Make the file polymorphic to be used in different contexts
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_type_name = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.file_name