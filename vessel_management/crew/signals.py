# crew/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import CrewCertificate, CertificateNotification


@receiver(post_save, sender=CrewCertificate)
def check_certificate_expiry(sender, instance, created, **kwargs):
    """
    When a certificate is created or updated, check if it's close to expiry
    and create notifications if needed.
    """
    if not created and not kwargs.get('raw', False):
        return  # Only run for newly created certificates
    
    today = timezone.now().date()
    days_thresholds = [30, 60, 90]  # Notify at 90, 60, and 30 days before expiry
    
    for days in days_thresholds:
        days_until_expiry = (instance.expiry_date - today).days
        
        # If the certificate is expiring within our threshold window
        if 0 <= days_until_expiry <= days:
            # Check if we already have a notification for this threshold
            notification_exists = CertificateNotification.objects.filter(
                certificate=instance,
                days_before_expiry=days
            ).exists()
            
            if not notification_exists:
                # Create a notification
                message = f"Certificate '{instance.certificate_name}' for {instance.crew.name} will expire in {days_until_expiry} days on {instance.expiry_date}."
                CertificateNotification.objects.create(
                    certificate=instance,
                    days_before_expiry=days,
                    message=message,
                    sent_to=instance.crew.email
                )