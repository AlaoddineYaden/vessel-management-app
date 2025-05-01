from django.db import models
from django.conf import settings
from django.utils import timezone
import os

class ReportType(models.TextChoices):
    VESSEL_COMPLIANCE = 'vessel_compliance', 'Vessel Compliance'
    MAINTENANCE_STATUS = 'maintenance_status', 'Maintenance Status'
    CERTIFICATION = 'certification', 'Certification Status'
    FUEL_CONSUMPTION = 'fuel_consumption', 'Fuel Consumption'
    CREW_ROSTER = 'crew_roster', 'Crew Roster'
    CUSTOM = 'custom', 'Custom Report'


class Report(models.Model):
    """Definition of available reports in the system"""
    name = models.CharField(max_length=100)
    report_type = models.CharField(
        max_length=50,
        choices=ReportType.choices,
        default=ReportType.CUSTOM
    )
    description = models.TextField(blank=True)
    query_parameters = models.JSONField(default=dict)
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class SavedReport(models.Model):
    """Stored results of generated reports"""
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    parameters_used = models.JSONField(default=dict)
    result_data = models.JSONField()
    file_format = models.CharField(max_length=10, default='json')
    file_location = models.CharField(max_length=255, blank=True, null=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    generated_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Results for {self.report.name} ({self.generated_date})"


class ReportSchedule(models.Model):
    """Schedule configuration for recurring reports"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    parameters = models.JSONField(default=dict)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    time_of_day = models.TimeField()
    day_of_week = models.IntegerField(blank=True, null=True)  # For weekly reports
    day_of_month = models.IntegerField(blank=True, null=True)  # For monthly reports
    output_format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    recipients = models.JSONField(default=list)  # List of email addresses
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_date = models.DateTimeField(auto_now_add=True)
    last_run = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.frequency})"

    def generate_report(self):
        """Generate report data based on the schedule's parameters"""
        from .tasks import generate_report
        
        # Generate the report using the task function
        report_data = generate_report(self.report.id, self.parameters)
        
        return report_data

    def save_report(self, report_data):
        """Save the generated report to the database and file system"""
        # Create SavedReport instance
        saved_report = SavedReport.objects.create(
            report=self.report,
            parameters_used=self.parameters,
            result_data=report_data,
            file_format=self.output_format,
            generated_by=self.created_by
        )
        
        # Export the report data
        from .services.exporters import ExporterFactory
        exporter = ExporterFactory.create_exporter(self.output_format)
        exported_data = exporter.export(report_data)
        
        # Create file name and path
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"{self.name}_{timestamp}.{self.output_format.lower()}"
        file_path = os.path.join(settings.REPORTS_DIR, file_name)
        
        # Ensure directory exists
        os.makedirs(settings.REPORTS_DIR, exist_ok=True)
        
        # Write the file based on format
        if self.output_format.upper() == 'PDF':
            # For PDF, write binary data directly
            with open(file_path, 'wb') as f:
                f.write(exported_data)
        else:
            # For text formats (JSON, CSV), write text data
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(exported_data)
        
        # Save the file location
        saved_report.file_location = f"reports/{file_name}"
        saved_report.save()
        
        return saved_report


class DashboardMetric(models.Model):
    """Configurable metrics for dashboard display"""
    METRIC_TYPES = [
        ('count', 'Count'),
        ('percentage', 'Percentage'),
        ('average', 'Average'),
        ('sum', 'Sum'),
        ('min', 'Minimum'),
        ('max', 'Maximum'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    data_source = models.CharField(max_length=100)
    query_definition = models.JSONField(default=dict)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    refresh_interval_minutes = models.IntegerField(default=60)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_date = models.DateTimeField(auto_now_add=True)
    last_calculated = models.DateTimeField(blank=True, null=True)
    last_value = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name 