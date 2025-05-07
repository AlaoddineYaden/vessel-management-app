# models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import BaseModel, Vessel

class NonConformity(BaseModel):
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('CLOSED', 'Closed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    SOURCE_CHOICES = [
        ('INSPECTION', 'Inspection'),
        ('AUDIT', 'Audit'),
        ('COMPLAINT', 'Complaint'),
        ('INCIDENT', 'Incident'),
        ('OTHER', 'Other'),
    ]
    
    description = models.TextField()
    detection_date = models.DateField()
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    source_id = models.CharField(max_length=100, blank=True, null=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, related_name='non_conformities')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    root_cause = models.TextField(blank=True, null=True)
    reference_documents = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"NC-{self.id}: {self.description[:50]}"

class CorrectiveAction(BaseModel):
    VERIFICATION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    ]
    
    non_conformity = models.ForeignKey(NonConformity, on_delete=models.CASCADE, related_name='corrective_actions')
    description = models.TextField()
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='assigned_corrective_actions')
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='PENDING')
    verification_comments = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"CA-{self.id}: {self.description[:50]}"
    
    @property
    def is_overdue(self):
        if self.completed_date:
            return False
        return self.due_date < timezone.now().date()

class EvidenceFile(BaseModel):
    corrective_action = models.ForeignKey(CorrectiveAction, on_delete=models.CASCADE, related_name='evidence_files')
    file = models.FileField(upload_to='evidence_files/')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Evidence-{self.id}: {self.file.name}"

class PreventiveAction(BaseModel):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    non_conformity = models.ForeignKey(NonConformity, on_delete=models.CASCADE, related_name='preventive_actions')
    description = models.TextField()
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='assigned_preventive_actions')
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    completed_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"PA-{self.id}: {self.description[:50]}"

class NCAttachment(BaseModel):
    """
    Model for storing attachments related to non-conformities.
    """
    non_conformity = models.ForeignKey(NonConformity, on_delete=models.CASCADE, related_name='attachments')
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='nc_attachments/')
    file_type = models.CharField(max_length=50)
    file_size = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.file_name} - NC-{self.non_conformity.id}"

class NCComment(BaseModel):
    """
    Model for storing comments on non-conformities.
    """
    non_conformity = models.ForeignKey(NonConformity, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='nc_comments')
    comment = models.TextField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user} on NC-{self.non_conformity.id}"

class NCHistory(BaseModel):
    """
    Model for tracking history of changes to non-conformities.
    """
    ACTION_CHOICES = [
        ('CREATED', 'Created'),
        ('UPDATED', 'Updated'),
        ('STATUS_CHANGED', 'Status Changed'),
        ('ASSIGNED', 'Assigned'),
        ('CLOSED', 'Closed'),
        ('CANCELLED', 'Cancelled'),
        ('COMMENT_ADDED', 'Comment Added'),
        ('ATTACHMENT_ADDED', 'Attachment Added'),
    ]
    
    non_conformity = models.ForeignKey(NonConformity, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='nc_history_entries')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} on NC-{self.non_conformity.id} by {self.user}"
