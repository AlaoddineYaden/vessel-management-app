from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, time

from vessel_reporting.models import Report, ReportSchedule, DashboardMetric

class Command(BaseCommand):
    help = 'Populates the database with sample vessel reporting data'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Create admin user if not exists
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        # Sample reports data
        sample_reports = [
            {
                'name': 'Monthly Maintenance Report',
                'report_type': 'MAINTENANCE',
                'description': 'Monthly summary of maintenance activities and status',
                'query_parameters': {
                    'vessel_id': 1,
                    'date_range': 'last_month',
                    'include_details': True
                },
                'is_public': True
            },
            {
                'name': 'Certificate Expiry Report',
                'report_type': 'CERTIFICATE',
                'description': 'List of certificates expiring in the next 30 days',
                'query_parameters': {
                    'vessel_id': 1,
                    'days_until_expiry': 30,
                    'include_crew': True
                },
                'is_public': False
            },
            {
                'name': 'ISM Compliance Report',
                'report_type': 'COMPLIANCE',
                'description': 'ISM compliance status and findings',
                'query_parameters': {
                    'vessel_id': 1,
                    'include_reviews': True,
                    'include_evidence': True
                },
                'is_public': False
            },
            {
                'name': 'Crew Certification Report',
                'report_type': 'CREW',
                'description': 'Crew certification status and training requirements',
                'query_parameters': {
                    'vessel_id': 1,
                    'include_expired': True,
                    'include_upcoming': True
                },
                'is_public': False
            },
            {
                'name': 'Safety Incident Report',
                'report_type': 'SAFETY',
                'description': 'Safety incidents and near-misses report',
                'query_parameters': {
                    'vessel_id': 1,
                    'date_range': 'last_quarter',
                    'include_investigations': True
                },
                'is_public': True
            }
        ]

        # Create reports
        reports = []
        for report_data in sample_reports:
            report = Report.objects.create(
                **report_data,
                created_by=admin_user
            )
            reports.append(report)
            self.stdout.write(self.style.SUCCESS(f'Created report: {report}'))

        # Sample report schedules
        report_schedules = [
            {
                'name': 'Daily Maintenance Report',
                'frequency': 'daily',
                'time_of_day': time(8, 0),  # 8:00 AM
                'output_format': 'pdf',
                'recipients': ['operations@example.com', 'maintenance@example.com'],
                'parameters': {'vessel_id': 1, 'include_details': True}
            },
            {
                'name': 'Weekly Certificate Check',
                'frequency': 'weekly',
                'time_of_day': time(9, 0),  # 9:00 AM
                'day_of_week': 1,  # Monday
                'output_format': 'csv',
                'recipients': ['safety@example.com', 'crew@example.com'],
                'parameters': {'vessel_id': 1, 'days_until_expiry': 30}
            },
            {
                'name': 'Monthly Compliance Report',
                'frequency': 'monthly',
                'time_of_day': time(10, 0),  # 10:00 AM
                'day_of_month': 1,  # First day of month
                'output_format': 'pdf',
                'recipients': ['compliance@example.com', 'management@example.com'],
                'parameters': {'vessel_id': 1, 'include_reviews': True}
            }
        ]

        # Create report schedules
        for report, schedule_data in zip(reports[:3], report_schedules):
            schedule = ReportSchedule.objects.create(
                report=report,
                **schedule_data,
                created_by=admin_user
            )
            self.stdout.write(self.style.SUCCESS(f'Created report schedule: {schedule}'))

        # Sample dashboard metrics
        dashboard_metrics = [
            {
                'name': 'Certificate Compliance Rate',
                'description': 'Percentage of valid certificates',
                'metric_type': 'percentage',
                'data_source': 'certificates',
                'query_definition': {
                    'valid_certificates': {'status': 'VALID'},
                    'total_certificates': {'status__in': ['VALID', 'EXPIRED']}
                },
                'display_order': 1,
                'refresh_interval_minutes': 60
            },
            {
                'name': 'Maintenance Completion Rate',
                'description': 'Percentage of completed maintenance tasks',
                'metric_type': 'percentage',
                'data_source': 'maintenance',
                'query_definition': {
                    'completed_tasks': {'status': 'COMPLETED'},
                    'total_tasks': {'status__in': ['COMPLETED', 'PENDING']}
                },
                'display_order': 2,
                'refresh_interval_minutes': 30
            },
            {
                'name': 'ISM Compliance Score',
                'description': 'Overall ISM compliance score',
                'metric_type': 'percentage',
                'data_source': 'ism_compliance',
                'query_definition': {
                    'compliant_items': {'status': 'COMPLIANT'},
                    'total_items': {'status__in': ['COMPLIANT', 'NON_COMPLIANT']}
                },
                'display_order': 3,
                'refresh_interval_minutes': 120
            },
            {
                'name': 'Safety Incidents',
                'description': 'Number of safety incidents in the last 30 days',
                'metric_type': 'count',
                'data_source': 'safety',
                'query_definition': {
                    'date_range': 'last_30_days',
                    'incident_types': ['INCIDENT', 'NEAR_MISS']
                },
                'display_order': 4,
                'refresh_interval_minutes': 60
            }
        ]

        # Create dashboard metrics
        for metric_data in dashboard_metrics:
            metric = DashboardMetric.objects.create(
                **metric_data,
                created_by=admin_user
            )
            self.stdout.write(self.style.SUCCESS(f'Created dashboard metric: {metric}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated Vessel Reporting with sample data')) 