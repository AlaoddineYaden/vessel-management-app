from django.core.management.base import BaseCommand
from django.utils import timezone
from vessel_reporting.models import Report, SavedReport, ReportSchedule, DashboardMetric
from core.models import Vessel
from django.contrib.auth import get_user_model
from datetime import timedelta, time

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample vessel reporting data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding vessel reporting data...')

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        SavedReport.objects.all().delete()
        Report.objects.all().delete()
        ReportSchedule.objects.all().delete()
        DashboardMetric.objects.all().delete()
        self.stdout.write('Existing data cleared')

        # Get the vessel
        vessel = Vessel.objects.first()
        if not vessel:
            self.stdout.write(self.style.ERROR('No vessels found in the database. Please create a vessel first.'))
            return

        # Get or create a system user
        system_user, created = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            system_user.set_password('system123')
            system_user.save()
            self.stdout.write('Created system user for reporting')

        # Create reports
        reports = [
            {
                'name': 'Daily Noon Report',
                'report_type': 'fuel_consumption',
                'description': 'Daily vessel position and performance report',
                'query_parameters': {
                    'time_range': 'daily',
                    'metrics': ['position', 'speed', 'fuel_consumption']
                },
                'is_public': True,
                'created_by': system_user
            },
            {
                'name': 'Weekly Safety Report',
                'report_type': 'custom',
                'description': 'Weekly summary of safety incidents and drills',
                'query_parameters': {
                    'time_range': 'weekly',
                    'metrics': ['incidents', 'drills', 'near_misses']
                },
                'is_public': True,
                'created_by': system_user
            },
            {
                'name': 'Monthly Performance Report',
                'report_type': 'custom',
                'description': 'Monthly vessel performance and efficiency report',
                'query_parameters': {
                    'time_range': 'monthly',
                    'metrics': ['fuel_efficiency', 'distance', 'cargo']
                },
                'is_public': True,
                'created_by': system_user
            }
        ]

        created_reports = {}
        for report_data in reports:
            try:
                report = Report.objects.create(**report_data)
                created_reports[report.name] = report
                self.stdout.write(f'Created report: {report.name}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating report {report_data["name"]}: {str(e)}')
                )

        # Create report schedules
        schedules = [
            {
                'report': created_reports['Daily Noon Report'],
                'name': 'Daily Noon Report Schedule',
                'parameters': {'time_zone': 'UTC'},
                'frequency': 'daily',
                'time_of_day': time(12, 0),  # 12:00
                'output_format': 'json',
                'recipients': ['captain@vessel.com', 'operations@company.com'],
                'is_active': True,
                'created_by': system_user
            },
            {
                'report': created_reports['Weekly Safety Report'],
                'name': 'Weekly Safety Report Schedule',
                'parameters': {'include_attachments': True},
                'frequency': 'weekly',
                'time_of_day': time(16, 0),  # 16:00
                'day_of_week': 1,  # Monday
                'output_format': 'pdf',
                'recipients': ['safety@company.com', 'captain@vessel.com'],
                'is_active': True,
                'created_by': system_user
            },
            {
                'report': created_reports['Monthly Performance Report'],
                'name': 'Monthly Performance Report Schedule',
                'parameters': {'detailed': True},
                'frequency': 'monthly',
                'time_of_day': time(9, 0),  # 09:00
                'day_of_month': 1,
                'output_format': 'pdf',
                'recipients': ['management@company.com', 'technical@company.com'],
                'is_active': True,
                'created_by': system_user
            }
        ]

        for schedule_data in schedules:
            try:
                schedule = ReportSchedule.objects.create(**schedule_data)
                self.stdout.write(f'Created report schedule: {schedule.name}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating schedule {schedule_data["name"]}: {str(e)}')
                )

        # Create saved reports
        today = timezone.now()
        saved_reports = [
            {
                'report': created_reports['Daily Noon Report'],
                'parameters_used': {'date': '2023-12-01'},
                'result_data': {
                    'position': {'lat': '1.2345 N', 'lon': '103.8765 E'},
                    'speed': 12.5,
                    'fuel_consumption': 45.6
                },
                'file_format': 'json',
                'generated_by': system_user
            },
            {
                'report': created_reports['Weekly Safety Report'],
                'parameters_used': {'week': '48'},
                'result_data': {
                    'incidents': 0,
                    'near_misses': 2,
                    'drills_completed': ['Fire Drill', 'Abandon Ship']
                },
                'file_format': 'pdf',
                'generated_by': system_user
            },
            {
                'report': created_reports['Monthly Performance Report'],
                'parameters_used': {'month': '11', 'year': '2023'},
                'result_data': {
                    'distance_traveled': 8750,
                    'fuel_consumed': 1250,
                    'efficiency_metrics': {
                        'fuel_efficiency': 0.14,
                        'speed_efficiency': 0.92
                    }
                },
                'file_format': 'pdf',
                'generated_by': system_user
            }
        ]

        for saved_data in saved_reports:
            try:
                saved = SavedReport.objects.create(**saved_data)
                self.stdout.write(f'Created saved report for: {saved.report.name}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating saved report for {saved_data["report"].name}: {str(e)}')
                )

        # Create dashboard metrics
        metrics = [
            {
                'name': 'Average Daily Fuel Consumption',
                'description': 'Average fuel consumption over the last 30 days',
                'metric_type': 'average',
                'data_source': 'noon_reports',
                'query_definition': {
                    'field': 'fuel_consumption',
                    'period': '30d',
                    'aggregation': 'avg'
                },
                'display_order': 1,
                'is_active': True,
                'refresh_interval_minutes': 60,
                'created_by': system_user
            },
            {
                'name': 'Safety Incidents This Month',
                'description': 'Count of safety incidents in the current month',
                'metric_type': 'count',
                'data_source': 'safety_reports',
                'query_definition': {
                    'field': 'incidents',
                    'period': 'this_month',
                    'aggregation': 'sum'
                },
                'display_order': 2,
                'is_active': True,
                'refresh_interval_minutes': 30,
                'created_by': system_user
            },
            {
                'name': 'Fleet Efficiency Score',
                'description': 'Overall fleet efficiency based on multiple factors',
                'metric_type': 'percentage',
                'data_source': 'performance_reports',
                'query_definition': {
                    'fields': ['fuel_efficiency', 'speed_efficiency'],
                    'period': 'this_month',
                    'aggregation': 'weighted_avg'
                },
                'display_order': 3,
                'is_active': True,
                'refresh_interval_minutes': 120,
                'created_by': system_user
            }
        ]

        for metric_data in metrics:
            try:
                metric = DashboardMetric.objects.create(**metric_data)
                self.stdout.write(f'Created dashboard metric: {metric.name}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating metric {metric_data["name"]}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded vessel reporting data')) 