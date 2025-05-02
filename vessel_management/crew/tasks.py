from celery import shared_task
from django.utils import timezone
from .models import CrewCertificate, CertificateNotification
from datetime import timedelta

@shared_task
def generate_certificate_notifications():
    """Generate notifications for certificates expiring soon"""
    today = timezone.now().date()
    notifications_created = 0
    
    # First check expired certificates
    expired_certs = CrewCertificate.objects.filter(expiry_date__lt=today)
    for cert in expired_certs:
        days_expired = (today - cert.expiry_date).days
        
        # Delete any existing notifications for this certificate
        CertificateNotification.objects.filter(certificate=cert).delete()
        
        # Create a new notification for expired certificate
        message = f"⚠️ URGENT: Certificate '{cert.certificate_name}' for {cert.crew.name} has been expired for {days_expired} days. Please renew immediately!"
        CertificateNotification.objects.create(
            certificate=cert,
            days_before_expiry=0,
            message=message,
            sent_to=cert.crew.email
        )
        notifications_created += 1
    
    # Then check certificates expiring within 90 days
    expiring_certs = CrewCertificate.objects.filter(
        expiry_date__gt=today,
        expiry_date__lte=today + timedelta(days=90)
    )
    
    for cert in expiring_certs:
        days_until_expiry = (cert.expiry_date - today).days
        
        # Determine which threshold we're at (90, 60, or 30 days)
        threshold = None
        if 0 <= days_until_expiry <= 30:
            threshold = 30
        elif 31 <= days_until_expiry <= 60:
            threshold = 60
        elif 61 <= days_until_expiry <= 90:
            threshold = 90
        
        if threshold is not None:
            # Delete any existing notifications for this certificate
            CertificateNotification.objects.filter(certificate=cert).delete()
            
            # Create a new notification for the current threshold
            urgency = "⚠️ URGENT" if threshold == 30 else "⚠️" if threshold == 60 else ""
            message = f"{urgency} Certificate '{cert.certificate_name}' for {cert.crew.name} will expire in {days_until_expiry} days on {cert.expiry_date}."
            CertificateNotification.objects.create(
                certificate=cert,
                days_before_expiry=threshold,
                message=message,
                sent_to=cert.crew.email
            )
            notifications_created += 1
    
    return notifications_created