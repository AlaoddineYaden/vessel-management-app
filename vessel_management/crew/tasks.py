from celery import shared_task
from django.utils import timezone
from .models import CrewCertificate, CertificateNotification
from datetime import timedelta

@shared_task
def generate_certificate_notifications():
    """Generate notifications for certificates expiring soon"""
    days_thresholds = [30, 60, 90]  # Notify at 90, 60, and 30 days before expiry
    today = timezone.now().date()
    notifications_created = 0
    
    for days in days_thresholds:
        target_date = today + timedelta(days=days)
        # Find certificates expiring on the target date
        expiring_certs = CrewCertificate.objects.filter(
            expiry_date=target_date
        )
        
        for cert in expiring_certs:
            # Check if notification already exists for this certificate and threshold
            notification_exists = CertificateNotification.objects.filter(
                certificate=cert,
                days_before_expiry=days
            ).exists()
            
            if not notification_exists:
                # Create notification
                message = f"Certificate '{cert.certificate_name}' for {cert.crew.name} will expire in {days} days on {cert.expiry_date}."
                CertificateNotification.objects.create(
                    certificate=cert,
                    days_before_expiry=days,
                    message=message,
                    sent_to=cert.crew.email
                )
                notifications_created += 1
    
    return notifications_created