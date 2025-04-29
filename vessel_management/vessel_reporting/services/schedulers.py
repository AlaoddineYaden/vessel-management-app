from datetime import datetime, timedelta
from django.utils import timezone
from ..models import ReportSchedule, SavedReport
from .exporters import ExporterFactory


class ReportScheduler:
    """Handles report scheduling and execution"""
    
    @staticmethod
    def get_reports_due_for_execution():
        """Get all reports that are due for execution"""
        current_time = timezone.now()
        return ReportSchedule.objects.filter(
            is_active=True,
            last_run__lt=current_time - timedelta(days=1)
        )
    
    @staticmethod
    def is_schedule_due(schedule, current_time):
        """Check if a schedule is due for execution"""
        if not schedule.is_active:
            return False
        
        # Check if it's the right time of day
        schedule_time = schedule.time_of_day
        if current_time.time() < schedule_time:
            return False
        
        # Check frequency-specific conditions
        if schedule.frequency == 'daily':
            return True
        
        elif schedule.frequency == 'weekly':
            return current_time.weekday() == schedule.day_of_week
        
        elif schedule.frequency == 'monthly':
            return current_time.day == schedule.day_of_month
        
        elif schedule.frequency == 'quarterly':
            # Check if it's the first day of a quarter
            return (current_time.month in [1, 4, 7, 10] and 
                   current_time.day == schedule.day_of_month)
        
        return False


class ReportDelivery:
    """Handles report delivery to recipients"""
    
    @staticmethod
    def deliver_report(saved_report, schedule):
        """Deliver a report to its recipients"""
        # This would be implemented with actual email sending logic
        # For now, we return a mock implementation
        return {
            'method': 'deliver_report',
            'report_id': saved_report.id,
            'recipients': schedule.recipients,
            'timestamp': timezone.now().isoformat()
        } 