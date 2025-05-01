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
from django.conf import settings


def generate_report(report_id, parameters):
    """Generate report data based on report type and parameters"""
    report = Report.objects.get(id=report_id)
    
    # Generate report data based on report type
    if report.report_type == 'vessel_compliance':
        return ComplianceMetrics.generate_report(parameters)
    elif report.report_type == 'maintenance_status':
        return MaintenanceMetrics.generate_report(parameters)
    elif report.report_type == 'certification':
        return CertificationMetrics.generate_report(parameters)
    else:
        # For custom reports, return sample data
        return {
            'vessel_id': parameters.get('vessel_id', 1),
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
            exporter = ExporterFactory.create_exporter(report_data, schedule.output_format)
            exported_data = exporter.export(report_data)
            
            # Save the exported file
            file_name = f"report_{saved_report.id}.{schedule.output_format}"
            file_path = settings.REPORTS_DIR / file_name
            
            # Write the exported data to the file
            with open(file_path, 'w') as f:
                f.write(exported_data)
            
            # Save the file location relative to MEDIA_ROOT
            saved_report.file_location = f"reports/{file_name}"
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