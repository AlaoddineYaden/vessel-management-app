# certificates/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Certificate, CertificateRenewal

@receiver(post_save, sender=Certificate)
def update_certificate_status(sender, instance, created, **kwargs):
    """Update certificate status based on expiry date"""
    if not created:  # Skip for newly created certificates (status already set in save method)
        return
    
    today = timezone.now().date()
    days_to_expiry = (instance.expiry_date - today).days
    
    if instance.status not in ['revoked', 'suspended', 'pending']:
        status_changed = False
        
        if days_to_expiry <= 0:
            instance.status = 'expired'
            status_changed = True
        elif days_to_expiry <= 30:  # 30 days warning period
            instance.status = 'expiring_soon'
            status_changed = True
            
        if status_changed:
            # Use update to avoid recursive signal triggering
            Certificate.objects.filter(pk=instance.pk).update(status=instance.status)