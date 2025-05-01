from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import os
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
        # Prepare email content
        subject = f"Report: {saved_report.report.name}"
        
        # Get the full file path
        file_path = os.path.join(settings.MEDIA_ROOT, saved_report.file_location)
        
        # Read the report file
        with open(file_path, 'rb') as file:
            report_content = file.read()
        
        # Create email message with HTML template
        context = {
            'report_name': saved_report.report.name,
            'generated_at': saved_report.generated_date.strftime('%Y-%m-%d %H:%M:%S'),
            'frequency': schedule.frequency,
            'format': schedule.output_format.upper()
        }
        
        html_content = f"""
        <html>
        <body>
            <h2>Vessel Management System - Report Delivery</h2>
            <p>Please find attached the {context['report_name']} report.</p>
            
            <h3>Report Details:</h3>
            <ul>
                <li><strong>Generated:</strong> {context['generated_at']}</li>
                <li><strong>Schedule:</strong> {context['frequency'].title()}</li>
                <li><strong>Format:</strong> {context['format']}</li>
            </ul>
            
            <p>If you have any questions about this report, please contact the system administrator.</p>
            
            <hr>
            <small>This is an automated message from the Vessel Management System.</small>
        </body>
        </html>
        """
        
        # Create email message
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=None,  # Will use DEFAULT_FROM_EMAIL
            to=schedule.recipients,
        )
        
        # Set the content type to HTML
        email.content_subtype = "html"
        
        # Attach the report file
        file_name = f"{saved_report.report.name}_{timezone.now().strftime('%Y%m%d')}.{saved_report.file_format}"
        email.attach(file_name, report_content, f'application/{saved_report.file_format}')
        
        # Send the email
        email.send() 