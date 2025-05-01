from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Core Models
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='%(class)s_created',
        null=True, blank=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='%(class)s_updated',
        null=True, blank=True
    )
    
    class Meta:
        abstract = True

class Vessel(BaseModel):
    name = models.CharField(max_length=255)
    imo_number = models.CharField(max_length=20, unique=True)
    mmsi_number = models.CharField(max_length=20, blank=True, null=True)
    call_sign = models.CharField(max_length=20, blank=True, null=True)
    vessel_type = models.CharField(max_length=100)
    flag = models.CharField(max_length=100)
    build_year = models.PositiveIntegerField()
    length_overall = models.DecimalField(max_digits=10, decimal_places=2)
    beam = models.DecimalField(max_digits=10, decimal_places=2)
    draft = models.DecimalField(max_digits=10, decimal_places=2)
    gross_tonnage = models.DecimalField(max_digits=10, decimal_places=2)
    net_tonnage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} (IMO: {self.imo_number})"

class SystemLog(BaseModel):
    class LogLevel(models.TextChoices):
        INFO = 'INFO', _('Info')
        WARNING = 'WARNING', _('Warning')
        ERROR = 'ERROR', _('Error')
        CRITICAL = 'CRITICAL', _('Critical')
    
    level = models.CharField(max_length=10, choices=LogLevel.choices, default=LogLevel.INFO)
    message = models.TextField()
    source = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='log_entries',
        null=True, blank=True
    )
    
    def __str__(self):
        return f"{self.level} - {self.source} - {self.created_at}"

class File(BaseModel):
    file = models.FileField(upload_to='documents/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_size = models.PositiveIntegerField()
    content_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_type_name = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.file_name

# Authentication Models
class UserProfile(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_company_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Vessel Reporting Models
class Report(BaseModel):
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=100)
    content = models.JSONField()
    status = models.CharField(max_length=50, default='draft')
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

class SavedReport(BaseModel):
    name = models.CharField(max_length=255)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class ReportSchedule(BaseModel):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=50)
    next_run = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.report.title} - {self.frequency}"

class DashboardMetric(BaseModel):
    name = models.CharField(max_length=255)
    metric_type = models.CharField(max_length=100)
    query = models.TextField()
    refresh_interval = models.PositiveIntegerField()
    last_refresh = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name

# Vessel PMS Models
class Equipment(BaseModel):
    name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    manufacturer = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    installation_date = models.DateField()
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='operational')
    
    def __str__(self):
        return f"{self.name} - {self.serial_number}"

class MaintenanceTask(BaseModel):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=100)
    description = models.TextField()
    frequency = models.CharField(max_length=50)
    last_performed = models.DateField(null=True, blank=True)
    next_due = models.DateField()
    status = models.CharField(max_length=50, default='pending')
    
    def __str__(self):
        return f"{self.equipment.name} - {self.task_type}"

class MaintenanceHistory(BaseModel):
    task = models.ForeignKey(MaintenanceTask, on_delete=models.CASCADE)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    performed_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.task} - {self.performed_date}"

# Safety Procedures Models
class ProcedureCategory(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.name

class Procedure(BaseModel):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(ProcedureCategory, on_delete=models.CASCADE)
    content = models.TextField()
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=50, default='draft')
    effective_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.title

class ProcedureVersion(BaseModel):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    version = models.PositiveIntegerField()
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.procedure.title} - v{self.version}"

class ProcedureReview(BaseModel):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comments = models.TextField()
    status = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.procedure.title} - {self.reviewer.username}"

class ProcedureAcknowledgment(BaseModel):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    acknowledged_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.procedure.title}"

# ISM Compliance Models
class ISMRequirement(BaseModel):
    code = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.code} - {self.title}"

class ComplianceItem(BaseModel):
    requirement = models.ForeignKey(ISMRequirement, on_delete=models.CASCADE)
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.requirement.code} - {self.vessel.name}"

class ComplianceEvidence(BaseModel):
    compliance_item = models.ForeignKey(ComplianceItem, on_delete=models.CASCADE)
    evidence_type = models.CharField(max_length=100)
    description = models.TextField()
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.compliance_item} - {self.evidence_type}"

class ComplianceReview(BaseModel):
    compliance_item = models.ForeignKey(ComplianceItem, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    comments = models.TextField()
    
    def __str__(self):
        return f"{self.compliance_item} - {self.reviewer.username}"

# Non-Conformity Models
class NonConformity(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE)
    severity = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='open')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

class CorrectiveAction(BaseModel):
    non_conformity = models.ForeignKey(NonConformity, on_delete=models.CASCADE)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=50, default='pending')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.non_conformity.title} - Corrective Action"

class EvidenceFile(BaseModel):
    corrective_action = models.ForeignKey(CorrectiveAction, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.corrective_action} - Evidence"

class PreventiveAction(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE)
    due_date = models.DateField()
    status = models.CharField(max_length=50, default='pending')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

class NCAttachment(BaseModel):
    non_conformity = models.ForeignKey(NonConformity, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.non_conformity.title} - Attachment"

class NCComment(BaseModel):
    non_conformity = models.ForeignKey(NonConformity, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    
    def __str__(self):
        return f"{self.non_conformity.title} - Comment"

class NCHistory(BaseModel):
    non_conformity = models.ForeignKey(NonConformity, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.non_conformity.title} - {self.action}"

# Crew Models
class Crew(BaseModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=100)
    rank = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='active')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class CrewCertificate(BaseModel):
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE)
    certificate_type = models.CharField(max_length=255)
    certificate_number = models.CharField(max_length=255)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    issuing_authority = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.crew} - {self.certificate_type}"

class CrewAssignment(BaseModel):
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE)
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    position = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.crew} - {self.vessel.name}"

class CertificateNotification(BaseModel):
    crew_certificate = models.ForeignKey(CrewCertificate, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    notification_date = models.DateField()
    status = models.CharField(max_length=50, default='pending')
    
    def __str__(self):
        return f"{self.crew_certificate} - {self.notification_type}"

# Certificate Models
class CertificateType(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Certificate(BaseModel):
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE)
    certificate_type = models.ForeignKey(CertificateType, on_delete=models.CASCADE)
    certificate_number = models.CharField(max_length=255)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    issuing_authority = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='valid')
    
    def __str__(self):
        return f"{self.vessel.name} - {self.certificate_type.name}"

class CertificateRenewal(BaseModel):
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE)
    renewal_date = models.DateField()
    status = models.CharField(max_length=50, default='pending')
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.certificate} - Renewal"

# Audit and Inspection Models
class AuditType(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Audit(BaseModel):
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE)
    audit_type = models.ForeignKey(AuditType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=50, default='planned')
    auditor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.vessel.name} - {self.audit_type.name}"

class AuditFinding(BaseModel):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE)
    description = models.TextField()
    severity = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='open')
    corrective_action = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.audit} - Finding"

class InspectionItem(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class InspectionChecklist(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    items = models.ManyToManyField(InspectionItem)
    
    def __str__(self):
        return self.name

class Inspection(BaseModel):
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE)
    checklist = models.ForeignKey(InspectionChecklist, on_delete=models.CASCADE)
    inspection_date = models.DateField()
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='planned')
    
    def __str__(self):
        return f"{self.vessel.name} - {self.checklist.name}"

class InspectionResult(BaseModel):
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE)
    item = models.ForeignKey(InspectionItem, on_delete=models.CASCADE)
    result = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.inspection} - {self.item.name}"

class AuditNotification(BaseModel):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    notification_date = models.DateField()
    status = models.CharField(max_length=50, default='pending')
    
    def __str__(self):
        return f"{self.audit} - {self.notification_type}" 