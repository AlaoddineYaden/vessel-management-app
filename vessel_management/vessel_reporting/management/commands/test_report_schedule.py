from django.core.management.base import BaseCommand
from django.utils import timezone
from vessel_reporting.models import Report, ReportSchedule, SavedReport
from vessel_reporting.services.exporters import ExporterFactory
from vessel_reporting.services.schedulers import ReportScheduler

class Command(BaseCommand):
    help = 'Test report scheduling functionality'

    def handle(self, *args, **options):
        # Get the first report schedule
        schedule = ReportSchedule.objects.first()
        if not schedule:
            self.stdout.write(self.style.ERROR('No report schedules found. Please run populate_reporting_data first.'))
            return

        self.stdout.write(self.style.SUCCESS(f'Testing report schedule: {schedule}'))

        # Create scheduler instance
        scheduler = ReportScheduler()
        current_time = timezone.now()

        # Check if schedule is due
        if scheduler.is_schedule_due(schedule, current_time):
            self.stdout.write(self.style.SUCCESS('Schedule is due to run'))
        else:
            self.stdout.write(self.style.WARNING('Schedule is not due to run yet'))

        # Generate the report
        report_data = {
            'vessel_id': schedule.parameters.get('vessel_id', 1),
            'report_date': timezone.now().isoformat(),
            'data': {
                'maintenance_tasks': [
                    {'id': 1, 'description': 'Engine oil change', 'status': 'COMPLETED'},
                    {'id': 2, 'description': 'Fire extinguisher check', 'status': 'PENDING'}
                ],
                'certificates': [
                    {'id': 1, 'name': 'Safety Management Certificate', 'expiry_date': '2024-12-31'},
                    {'id': 2, 'name': 'Class Certificate', 'expiry_date': '2024-06-30'}
                ]
            }
        }

        # Create a saved report
        saved_report = SavedReport.objects.create(
            report=schedule.report,
            parameters_used=schedule.parameters,
            result_data=report_data,
            file_format=schedule.output_format,
            generated_by=schedule.created_by
        )

        # Export the report
        exporter = ExporterFactory.create_exporter(report_data, schedule.output_format)
        exported_data = exporter.export()

        # Save the exported file
        saved_report.file_location = f"reports/test_{saved_report.id}.{schedule.output_format}"
        saved_report.save()

        # Update last run time
        schedule.last_run = current_time
        schedule.save()

        self.stdout.write(self.style.SUCCESS(f'Report generated and saved: {saved_report}'))
        self.stdout.write(self.style.SUCCESS(f'Recipients: {schedule.recipients}'))
        self.stdout.write(self.style.SUCCESS(f'Format: {schedule.output_format}'))
        self.stdout.write(self.style.SUCCESS(f'Last run time updated to: {schedule.last_run}'))

        # In a real environment, this would send emails to recipients
        self.stdout.write(self.style.SUCCESS('In production, this would send emails to the recipients')) 