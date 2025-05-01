from django.core.management.base import BaseCommand
from django.utils import timezone
from vessel_reporting.models import ReportSchedule

class Command(BaseCommand):
    help = 'Check status of report schedules'

    def handle(self, *args, **options):
        # Get all schedules
        schedules = ReportSchedule.objects.all()
        self.stdout.write(f"Found {schedules.count()} total schedules\n")

        for schedule in schedules:
            self.stdout.write(
                f"\nSchedule: {schedule.name}"
                f"\n  Active: {schedule.is_active}"
                f"\n  Frequency: {schedule.frequency}"
                f"\n  Time of day: {schedule.time_of_day}"
                f"\n  Last run: {schedule.last_run}"
                f"\n  Recipients: {schedule.recipients}"
                f"\n  Output format: {schedule.output_format}"
            ) 