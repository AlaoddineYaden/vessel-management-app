# audit_inspection/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

User = get_user_model()

class AuditType(models.Model):
    """Model for different types of audits"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    frequency_days = models.PositiveIntegerField(
        help_text="Recommended frequency in days", 
        default=365
    )
    is_mandatory = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class Vessel(models.Model):
    """
    Placeholder for Vessel model - in a real application, this would 
    likely be imported from a core module rather than defined here
    """
    name = models.CharField(max_length=100)
    imo_number = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.name} (IMO: {self.imo_number})"


class Audit(models.Model):
    """Model for audit records"""
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('OVERDUE', 'Overdue'),
    ]
    
    audit_type = models.ForeignKey(AuditType, on_delete=models.PROTECT)
    planned_date = models.DateField()
    actual_date = models.DateField(blank=True, null=True)
    auditor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='conducted_audits')
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, related_name='audits')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')
    report_file = models.FileField(upload_to='audit_reports/', blank=True, null=True)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, 
        related_name='created_audits',
    )

    def __str__(self):
        return f"{self.audit_type} Audit - {self.vessel.name} ({self.planned_date})"
    
    def save(self, *args, **kwargs):
        # Update status to OVERDUE if planned date is past and status is still PLANNED
        if (self.status == 'PLANNED' and 
            self.planned_date < timezone.now().date()):
            self.status = 'OVERDUE'
        super().save(*args, **kwargs)
    
    def is_overdue(self):
        return (self.status == 'PLANNED' and 
                self.planned_date < timezone.now().date())


class AuditFinding(models.Model):
    """Model for recording specific findings during an audit"""
    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('MAJOR', 'Major'),
        ('MINOR', 'Minor'),
        ('OBSERVATION', 'Observation'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('CLOSED', 'Closed'),
        ('VERIFIED', 'Verified'),
    ]
    
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='findings')
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    due_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='assigned_findings'
    )
    corrective_action = models.TextField(blank=True)
    closed_date = models.DateField(null=True, blank=True)
    attachments = models.FileField(upload_to='finding_attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Finding {self.id} - {self.audit} - {self.severity}"
    
    def is_overdue(self):
        return (self.status in ['OPEN', 'IN_PROGRESS'] and 
                self.due_date and 
                self.due_date < timezone.now().date())


class InspectionItem(models.Model):
    """Model for standard inspection checklist items"""
    category = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    regulation_reference = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.category} - {self.name}"


class InspectionChecklist(models.Model):
    """Model for grouping inspection items into standard checklists"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    items = models.ManyToManyField(InspectionItem, related_name='checklists')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class Inspection(models.Model):
    """Model for inspection records"""
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('OVERDUE', 'Overdue'),
    ]
    
    checklist = models.ForeignKey(InspectionChecklist, on_delete=models.PROTECT)
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, related_name='inspections')
    inspector = models.ForeignKey(User, on_delete=models.PROTECT, related_name='conducted_inspections')
    planned_date = models.DateField()
    actual_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')
    comments = models.TextField(blank=True)
    report_file = models.FileField(upload_to='inspection_reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, 
        related_name='created_inspections',
    )

    def __str__(self):
        return f"Inspection - {self.vessel.name} - {self.checklist.name} ({self.planned_date})"
    
    def save(self, *args, **kwargs):
        # Update status to OVERDUE if planned date is past and status is still PLANNED
        if (self.status == 'PLANNED' and 
            self.planned_date < timezone.now().date()):
            self.status = 'OVERDUE'
        super().save(*args, **kwargs)


class InspectionResult(models.Model):
    """Model for recording results of individual inspection items"""
    RESULT_CHOICES = [
        ('COMPLIANT', 'Compliant'),
        ('NON_COMPLIANT', 'Non-Compliant'),
        ('NOT_APPLICABLE', 'Not Applicable'),
        ('NOT_CHECKED', 'Not Checked'),
    ]
    
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='results')
    item = models.ForeignKey(InspectionItem, on_delete=models.PROTECT)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    comments = models.TextField(blank=True)
    evidence_file = models.FileField(upload_to='inspection_evidence/', blank=True, null=True)
    
    class Meta:
        unique_together = ('inspection', 'item')
    
    def __str__(self):
        return f"{self.inspection} - {self.item.name} - {self.result}"


class AuditNotification(models.Model):
    """Model for tracking audit notifications"""
    NOTIFICATION_TYPE_CHOICES = [
        ('DUE_SOON', 'Due Soon'),
        ('OVERDUE', 'Overdue'),
        ('FINDING_DUE', 'Finding Due'),
        ('FINDING_OVERDUE', 'Finding Overdue'),
    ]
    
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, null=True, blank=True)
    finding = models.ForeignKey(AuditFinding, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    message = models.TextField()
    recipients = models.ManyToManyField(User, related_name='audit_notifications')
    is_sent = models.BooleanField(default=False)
    sent_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.audit:
            return f"{self.notification_type} - {self.audit}"
        return f"{self.notification_type} - {self.finding}"
