from celery import shared_task
from django.utils import timezone
from .models import Report, SavedReport, ReportSchedule, DashboardMetric
from .services.schedulers import ReportScheduler, ReportDelivery
from .services.exporters import ExporterFactory
from .services.metrics import (
    ComplianceMetrics,
    MaintenanceMetrics,
    CertificationMetrics
)


@shared_task
def execute_scheduled_reports():
    """Execute all reports that are due for execution"""
    scheduler = ReportScheduler()
    current_time = timezone.now()
    
    # Get all active schedules
    schedules = scheduler.get_reports_due_for_execution()
    
    for schedule in schedules:
        if scheduler.is_schedule_due(schedule, current_time):
            # Generate the report
            report_data = generate_report(schedule.report.id, schedule.parameters)
            
            # Create a saved report
            saved_report = SavedReport.objects.create(
                report=schedule.report,
                parameters_used=schedule.parameters,
                result_data=report_data,
                file_format=schedule.output_format,
                generated_by=schedule.created_by
            )
            
            # Export the report
            exporter = ExporterFactory.create_exporter(
                report_data,
                schedule.output_format
            )
            exported_data = exporter.export()
            
            # Save the exported file
            # This would be implemented with actual file storage logic
            saved_report.file_location = f"reports/{saved_report.id}.{schedule.output_format}"
            saved_report.save()
            
            # Deliver the report
            ReportDelivery.deliver_report(saved_report, schedule)
            
            # Update the schedule's last run time
            schedule.last_run = current_time
            schedule.save()


@shared_task
def refresh_dashboard_metrics():
    """Refresh all dashboard metrics"""
    metrics = DashboardMetric.objects.filter(is_active=True)
    
    for metric in metrics:
        # Calculate the metric value based on its type
        if metric.metric_type == 'compliance':
            calculator = ComplianceMetrics()
        elif metric.metric_type == 'maintenance':
            calculator = MaintenanceMetrics()
        elif metric.metric_type == 'certification':
            calculator = CertificationMetrics()
        else:
            continue
        
        # Calculate and update the metric
        result = calculator.calculate_metric(metric)
        metric.last_value = result
        metric.last_calculated = timezone.now()
        metric.save()


def generate_report(report_id, parameters=None):
    """Generate a report with the given parameters"""
    report = Report.objects.get(id=report_id)
    
    # This would be implemented with actual report generation logic
    # For now, we return a mock implementation
    return {
        'report_id': report_id,
        'parameters': parameters or {},
        'data': [
            {'id': 1, 'name': 'Sample Data 1'},
            {'id': 2, 'name': 'Sample Data 2'}
        ],
        'generated_at': timezone.now().isoformat()
    } 