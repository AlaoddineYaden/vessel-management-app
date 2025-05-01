from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from vessel_reporting.models import Report, ReportSchedule

class Command(BaseCommand):
    help = 'Create a test report schedule'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to receive the test report',
            required=True
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f"Created admin user: {admin_user.email}")
        
        # Create a test report
        report, created = Report.objects.get_or_create(
            name='Test Daily Report',
            defaults={
                'report_type': 'custom',
                'description': 'A test report for email delivery',
                'created_by': admin_user,
                'is_public': True,
            }
        )
        if created:
            self.stdout.write(f"Created test report: {report.name}")
        
        # Create a test schedule
        schedule, created = ReportSchedule.objects.get_or_create(
            name='Test Daily Schedule',
            defaults={
                'report': report,
                'frequency': 'daily',
                'time_of_day': timezone.now().time(),
                'output_format': 'pdf',
                'recipients': [options['email']],
                'is_active': True,
                'created_by': admin_user,
                'parameters': {
                    'test_data': True,
                    'include_details': True
                }
            }
        )
        if created:
            self.stdout.write(f"Created test schedule: {schedule.name}")
        else:
            # Update recipients if schedule already exists
            schedule.recipients = [options['email']]
            schedule.save()
            self.stdout.write(f"Updated test schedule recipients: {schedule.recipients}")
        
        self.stdout.write(self.style.SUCCESS('Test schedule setup completed successfully')) 