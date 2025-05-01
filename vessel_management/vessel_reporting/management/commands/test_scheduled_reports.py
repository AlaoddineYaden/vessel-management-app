from django.core.management.base import BaseCommand
from django.utils import timezone
from vessel_reporting.models import ReportSchedule
from vessel_reporting.services.schedulers import ReportScheduler, ReportDelivery
from vessel_reporting.services.exporters import ExporterFactory

class Command(BaseCommand):
    help = 'Test report scheduling functionality'

    def handle(self, *args, **options):
        # Get all active schedules
        schedules = ReportSchedule.objects.filter(is_active=True)
        self.stdout.write(f"Found {len(schedules)} active schedules\n")

        current_time = timezone.now()

        for schedule in schedules:
            self.stdout.write(f"\nProcessing schedule: {schedule.name} ({schedule.frequency})")
            
            try:
                # Generate the report
                report_data = schedule.generate_report()
                
                # Save the report
                saved_report = schedule.save_report(report_data)
                self.stdout.write(f"Report generated and saved: {saved_report}")
                
                # Deliver the report
                ReportDelivery.deliver_report(saved_report, schedule)
                self.stdout.write(f"Report sent to: {schedule.recipients}")
                self.stdout.write(f"Format: {schedule.output_format}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing report: {str(e)}"))
            
            # Update last run time
            schedule.last_run = current_time
            schedule.save()
            self.stdout.write(f"Last run time updated to: {schedule.last_run}") 