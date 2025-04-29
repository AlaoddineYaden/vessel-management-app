# crew/management/commands/generate_certificate_notifications.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from crew.models import CrewCertificate, CertificateNotification


class Command(BaseCommand):
    help = 'Generate notifications for certificates expiring soon'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            nargs='+',
            default=[30, 60, 90],
            help='Days thresholds for notification (default: 30, 60, 90)'
        )
        parser.add_argument(
            '--email',
            action='store_true',
            help='Send email notifications in addition to creating database records'
        )

    def handle(self, *args, **options):
        days_thresholds = options['days']
        send_emails = options['email']
        today = timezone.now().date()
        notifications_created = 0
        
        self.stdout.write(f"Checking for certificates expiring in {days_thresholds} days...")
        
        for days in days_thresholds:
            target_date = today + timedelta(days=days)
            # Find certificates expiring on the target date
            expiring_certs = CrewCertificate.objects.filter(
                expiry_date=target_date
            )
            
            self.stdout.write(f"Found {expiring_certs.count()} certificates expiring in {days} days")
            
            for cert in expiring_certs:
                # Check if notification already exists for this certificate and threshold
                notification_exists = CertificateNotification.objects.filter(
                    certificate=cert,
                    days_before_expiry=days
                ).exists()
                
                if not notification_exists:
                    # Create notification
                    message = f"Certificate '{cert.certificate_name}' for {cert.crew.name} will expire in {days} days on {cert.expiry_date}."
                    notification = CertificateNotification.objects.create(
                        certificate=cert,
                        days_before_expiry=days,
                        message=message,
                        sent_to=cert.crew.email
                    )
                    
                    self.stdout.write(f"Created notification for {cert.certificate_name} (ID: {cert.id})")
                    notifications_created += 1
                    
                    if send_emails:
                        try:
                            from django.core.mail import send_mail
                            from django.conf import settings
                            
                            send_mail(
                                subject=f"Certificate Expiry Alert: {cert.certificate_name}",
                                message=message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[cert.crew.email],
                                fail_silently=False,
                            )
                            
                            notification.status = 'SENT'
                            notification.save(update_fields=['status'])
                            self.stdout.write(f"Sent email notification to {cert.crew.email}")
                        except Exception as e:
                            self.stderr.write(f"Failed to send email: {str(e)}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated {notifications_created} new notifications')
        )