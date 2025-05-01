from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.utils import timezone
import os

class Command(BaseCommand):
    help = 'Test email sending functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipient',
            type=str,
            help='Email address of the recipient',
            required=True
        )

    def handle(self, *args, **options):
        recipient = options['recipient']
        
        # Create a test email
        subject = 'Test Email from Vessel Management System'
        body = f"""
        This is a test email sent from the Vessel Management System.
        
        Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
        Environment: {'Development' if os.getenv('DEBUG') == 'True' else 'Production'}
        
        If you received this email, the email configuration is working correctly.
        """
        
        try:
            # Send the email
            email = EmailMessage(
                subject=subject,
                body=body,
                to=[recipient],
            )
            email.send()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent test email to {recipient}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send email: {str(e)}')
            ) 