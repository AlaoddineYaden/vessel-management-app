from django.utils import timezone
from crew.models import CrewCertificate, CertificateNotification
from django.contrib.auth import get_user_model

class CertificateNotificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check notifications if user is authenticated
        if request.user.is_authenticated:
            self.update_notification_days()
            self.check_certificate_notifications(request.user)
        
        response = self.get_response(request)
        return response

    def update_notification_days(self):
        """Update days before expiry for all pending notifications"""
        today = timezone.now().date()
        
        # Get all pending notifications
        pending_notifications = CertificateNotification.objects.filter(
            status='PENDING'
        ).select_related('certificate')
        
        for notification in pending_notifications:
            if notification.certificate.expiry_date > today:
                # For expiring certificates
                days_until_expiry = (notification.certificate.expiry_date - today).days
                
                # Determine which threshold we're at (90, 60, or 30 days)
                threshold = None
                if 0 <= days_until_expiry <= 30:
                    threshold = 30
                elif 31 <= days_until_expiry <= 60:
                    threshold = 60
                elif 61 <= days_until_expiry <= 90:
                    threshold = 90
                
                if threshold is not None and threshold != notification.days_before_expiry:
                    # Update the notification with new days and message
                    notification.days_before_expiry = threshold
                    urgency = "⚠️ URGENT" if threshold == 30 else "⚠️" if threshold == 60 else ""
                    notification.message = f'{urgency} Certificate {notification.certificate.certificate_name} for {notification.certificate.crew.name} will expire in {days_until_expiry} days on {notification.certificate.expiry_date}.'
                    notification.save()
            else:
                # For expired certificates
                days_expired = (today - notification.certificate.expiry_date).days
                if notification.days_before_expiry != 0:
                    notification.days_before_expiry = 0
                    notification.message = f'⚠️ URGENT: Certificate {notification.certificate.certificate_name} for {notification.certificate.crew.name} has been expired for {days_expired} days. Please renew immediately!'
                    notification.save()

    def check_certificate_notifications(self, user):
        today = timezone.now().date()
        
        # Get a system user for created_by/updated_by fields
        User = get_user_model()
        system_user = User.objects.filter(is_superuser=True).first()
        
        # First check expired certificates
        expired_certificates = CrewCertificate.objects.filter(
            expiry_date__lt=today
        ).exclude(
            notifications__status='PENDING'
        )
        
        for certificate in expired_certificates:
            days_expired = (today - certificate.expiry_date).days
            
            # Create a new notification for expired certificate
            CertificateNotification.objects.create(
                certificate=certificate,
                days_before_expiry=0,
                status='PENDING',
                message=f'⚠️ URGENT: Certificate {certificate.certificate_name} for {certificate.crew.name} has been expired for {days_expired} days. Please renew immediately!',
                created_by=system_user,
                updated_by=system_user
            )
        
        # Then check expiring certificates (within 90 days)
        max_date = today + timezone.timedelta(days=90)
        expiring_certificates = CrewCertificate.objects.filter(
            expiry_date__gt=today,
            expiry_date__lte=max_date
        ).exclude(
            notifications__status='PENDING'
        )
        
        for certificate in expiring_certificates:
            days_until_expiry = (certificate.expiry_date - today).days
            
            # Determine which threshold we're at (90, 60, or 30 days)
            threshold = None
            if 0 <= days_until_expiry <= 30:
                threshold = 30
            elif 31 <= days_until_expiry <= 60:
                threshold = 60
            elif 61 <= days_until_expiry <= 90:
                threshold = 90
            
            if threshold is not None:
                # Create a new notification for the current threshold
                urgency = "⚠️ URGENT" if threshold == 30 else "⚠️" if threshold == 60 else ""
                CertificateNotification.objects.create(
                    certificate=certificate,
                    days_before_expiry=threshold,
                    status='PENDING',
                    message=f'{urgency} Certificate {certificate.certificate_name} for {certificate.crew.name} will expire in {days_until_expiry} days on {certificate.expiry_date}.',
                    created_by=system_user,
                    updated_by=system_user
                ) 