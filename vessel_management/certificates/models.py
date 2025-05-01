# certificates/models.py
from django.db import models
from django.utils import timezone
from django.conf import settings
from crew.models import Vessel  # Adjust the import path as needed

class CertificateType(models.Model):
    # No changes needed here
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_statutory = models.BooleanField(default=False)
    renewal_period_days = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name

class Certificate(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('expiring_soon', 'Expiring Soon'),
        ('revoked', 'Revoked'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending'),
    )
    
    certificate_name = models.CharField(max_length=255)
    certificate_type = models.ForeignKey(CertificateType, on_delete=models.PROTECT, related_name='certificates')
    certificate_number = models.CharField(max_length=100, unique=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    issuing_authority = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    # Make vessel field nullable to handle existing records
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, related_name='certificates', null=True, blank=True)
    document_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    # Rest of the model remains the same
    class Meta:
        ordering = ['-expiry_date']
        
    def __str__(self):
        return f"{self.certificate_name} - {self.certificate_number}"
    
    def save(self, *args, **kwargs):
        # Auto-update status based on expiry date
        today = timezone.now().date()
        days_to_expiry = (self.expiry_date - today).days
        old_status = self.status
        
        if self.status not in ['revoked', 'suspended', 'pending']:
            if days_to_expiry <= 0:
                self.status = 'expired'
            elif days_to_expiry <= 30:  # 30 days warning period
                self.status = 'expiring_soon'
            else:
                self.status = 'active'
                
        super().save(*args, **kwargs)
        
        # Create renewal record if certificate is expired or expiring soon
        if self.status in ['expired', 'expiring_soon']:
            CertificateRenewal.objects.get_or_create(
                certificate=self,
                defaults={
                    'status': 'pending',
                    'due_date': self.expiry_date,
                    'renewal_cost': None,
                    'notes': f'Certificate {self.status.replace("_", " ")} - renewal required',
                }
            )

# No changes needed to CertificateRenewal model
class CertificateRenewal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    )
    
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='renewals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    initiated_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    renewal_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Renewal for {self.certificate.certificate_name} ({self.certificate.certificate_number})"
    
    def save(self, *args, **kwargs):
        # Update status based on due date
        today = timezone.now().date()
        if self.status not in ['completed'] and today > self.due_date:
            self.status = 'overdue'
        super().save(*args, **kwargs)