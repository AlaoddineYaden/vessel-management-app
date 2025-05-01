from django.utils import timezone
from crew.models import CrewCertificate, CertificateNotification
from django.contrib.auth import get_user_model

class CertificateNotificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check notifications if user is authenticated
        if request.user.is_authenticated:
            self.check_certificate_notifications(request.user)
        
        response = self.get_response(request)
        return response

    def check_certificate_notifications(self, user):
        today = timezone.now().date()
        
        # Get a system user for created_by/updated_by fields
        User = get_user_model()
        system_user = User.objects.filter(is_superuser=True).first()
        
        # Check expiring certificates (within 90 days)
        max_date = today + timezone.timedelta(days=90)
        expiring_certificates = CrewCertificate.objects.filter(
            expiry_date__gt=today,
            expiry_date__lte=max_date
        ).exclude(
            notifications__status='PENDING'
        )
        
        for certificate in expiring_certificates:
            days_until_expiry = (certificate.expiry_date - today).days
            CertificateNotification.objects.get_or_create(
                certificate=certificate,
                days_before_expiry=days_until_expiry,
                defaults={
                    'status': 'PENDING',
                    'message': f'Certificate {certificate.certificate_name} for {certificate.crew.name} will expire in {days_until_expiry} days.',
                    'created_by': system_user,
                    'updated_by': system_user
                }
            )
        
        # Check expired certificates
        expired_certificates = CrewCertificate.objects.filter(
            expiry_date__lt=today
        ).exclude(
            notifications__status='PENDING'
        )
        
        for certificate in expired_certificates:
            days_expired = (today - certificate.expiry_date).days
            CertificateNotification.objects.get_or_create(
                certificate=certificate,
                days_before_expiry=0,
                defaults={
                    'status': 'PENDING',
                    'message': f'Certificate {certificate.certificate_name} for {certificate.crew.name} has been expired for {days_expired} days.',
                    'created_by': system_user,
                    'updated_by': system_user
                }
            ) 