from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
import os

def evidence_file_path(instance, filename):
    """Generate a unique file path for evidence documents"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('ism_compliance/evidence', filename)


class ISMRequirement(models.Model):
    """Model for storing ISM Code requirements"""
    ISM_SECTION_CHOICES = [
        ('1', '1 - General'),
        ('2', '2 - Safety and Environmental Protection Policy'),
        ('3', '3 - Company Responsibilities and Authority'),
        ('4', '4 - Designated Person(s)'),
        ('5', '5 - Master\'s Responsibility and Authority'),
        ('6', '6 - Resources and Personnel'),
        ('7', '7 - Development of Plans for Shipboard Operations'),
        ('8', '8 - Emergency Preparedness'),
        ('9', '9 - Reports and Analysis of Non-conformities, Accidents and Hazardous Occurrences'),
        ('10', '10 - Maintenance of the Ship and Equipment'),
        ('11', '11 - Documentation'),
        ('12', '12 - Company Verification, Review and Evaluation'),
        ('13', '13 - Certification, Verification and Control'),
        ('14', '14 - Interim Certification'),
        ('15', '15 - Verification'),
        ('16', '16 - Forms of Certificates'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ism_section = models.CharField(max_length=3, choices=ISM_SECTION_CHOICES)
    requirement_code = models.CharField(max_length=20, help_text="ISM code reference (e.g., '1.4.2')")
    requirement_text = models.TextField()
    guidance_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['ism_section', 'requirement_code']
        indexes = [
            models.Index(fields=['ism_section']),
            models.Index(fields=['requirement_code']),
        ]
        
    def __str__(self):
        return f"{self.requirement_code}: {self.requirement_text[:50]}..."


class ComplianceItem(models.Model):
    """Model for tracking compliance with ISM requirements per vessel"""
    STATUS_CHOICES = [
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('partially_compliant', 'Partially Compliant'),
        ('not_applicable', 'Not Applicable'),
        ('pending_review', 'Pending Review'),
    ]
    
    RISK_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ism_requirement = models.ForeignKey(ISMRequirement, on_delete=models.CASCADE, related_name='compliance_items')
    vessel_id = models.UUIDField(help_text="Reference to vessel in the main application")
    compliance_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_review')
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, default='medium')
    assessment_date = models.DateTimeField(default=timezone.now)
    next_review_date = models.DateTimeField(null=True, blank=True)
    assessor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assessed_items'
    )
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-assessment_date']
        indexes = [
            models.Index(fields=['vessel_id']),
            models.Index(fields=['compliance_status']),
            models.Index(fields=['assessment_date']),
        ]
        unique_together = ['ism_requirement', 'vessel_id']
        
    def __str__(self):
        return f"Compliance item for vessel {self.vessel_id} - {self.ism_requirement.requirement_code}"


class ComplianceEvidence(models.Model):
    """Model for storing evidence of compliance"""
    EVIDENCE_TYPE_CHOICES = [
        ('document', 'Document'),
        ('photo', 'Photograph'),
        ('record', 'Record'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    compliance_item = models.ForeignKey(ComplianceItem, on_delete=models.CASCADE, related_name='evidence')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    evidence_type = models.CharField(max_length=20, choices=EVIDENCE_TYPE_CHOICES)
    file = models.FileField(upload_to=evidence_file_path, null=True, blank=True)
    reference_url = models.URLField(blank=True, null=True, 
                                   help_text="URL reference to evidence in external system")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_evidence'
    )
    upload_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-upload_date']
        
    def __str__(self):
        return f"{self.title} - {self.evidence_type}"


class ComplianceReview(models.Model):
    """Model for tracking periodic reviews of compliance items"""
    REVIEW_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    compliance_item = models.ForeignKey(ComplianceItem, on_delete=models.CASCADE, related_name='reviews')
    scheduled_date = models.DateTimeField()
    actual_review_date = models.DateTimeField(null=True, blank=True)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='compliance_reviews'
    )
    status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='scheduled')
    findings = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['status']),
        ]
        
    def __str__(self):
        return f"Review for {self.compliance_item} on {self.scheduled_date}"
