# safety_procedures/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class ProcedureCategory(models.Model):
    """Categories for organizing procedures by ISM section"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, 
                              null=True, blank=True, related_name='subcategories')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Procedure Categories"
        ordering = ['order', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Procedure(models.Model):
    """Main model for safety procedures and ISM manuals"""
    DOCUMENT_TYPES = (
        ('PROCEDURE', 'Procedure'),
        ('CHECKLIST', 'Checklist'),
        ('MANUAL', 'Manual'),
        ('FORM', 'Form'),
        ('POLICY', 'Policy'),
    )
    
    REVIEW_STATUS = (
        ('CURRENT', 'Current'),
        ('DUE_SOON', 'Due Soon'),
        ('OVERDUE', 'Overdue'),
        ('IN_REVIEW', 'In Review'),
        ('DRAFT', 'Draft'),
    )
    
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    category = models.ForeignKey(ProcedureCategory, on_delete=models.PROTECT, 
                                related_name='procedures')
    content = models.TextField(blank=True)
    file_upload = models.FileField(upload_to='procedures/%Y/%m/', blank=True, null=True)
    version = models.CharField(max_length=20)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, 
                                  related_name='created_procedures')
    last_reviewed_date = models.DateTimeField(null=True, blank=True)
    next_review_date = models.DateTimeField(null=True, blank=True)
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS, default='DRAFT')
    review_interval_months = models.PositiveIntegerField(default=12)
    is_active = models.BooleanField(default=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.title} v{self.version}"
    
    def save(self, *args, **kwargs):
        """Override save to set next_review_date based on review interval"""
        if self.last_reviewed_date and not self.next_review_date:
            self.next_review_date = self.last_reviewed_date + relativedelta(months=self.review_interval_months)
        
        # Auto-update review status based on next_review_date
        if self.next_review_date:
            now = timezone.now()
            if self.review_status != 'IN_REVIEW' and self.review_status != 'DRAFT':
                if self.next_review_date < now:
                    self.review_status = 'OVERDUE'
                elif (self.next_review_date - now).days < 30:
                    self.review_status = 'DUE_SOON'
                else:
                    self.review_status = 'CURRENT'
        
        super().save(*args, **kwargs)
    
    def create_new_version(self, new_version, user):
        """Create a new version of this procedure"""
        old_id = self.id
        # Make a copy of the current procedure
        self.pk = None  # Create a new instance
        self.version = new_version
        self.created_date = timezone.now()
        self.created_by = user
        self.last_reviewed_date = timezone.now()
        self.next_review_date = self.last_reviewed_date + relativedelta(months=self.review_interval_months)
        self.review_status = 'CURRENT'
        self.save()
        
        # Create a version history entry
        ProcedureVersion.objects.create(
            procedure_id=self.id,
            previous_procedure_id=old_id,
            version=new_version,
            created_by=user
        )
        
        return self


class ProcedureVersion(models.Model):
    """Track procedure version history"""
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name='versions')
    previous_procedure = models.ForeignKey(Procedure, on_delete=models.SET_NULL, 
                                         null=True, related_name='next_versions')
    version = models.CharField(max_length=20)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    change_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.procedure.title} v{self.version}"


class ProcedureReview(models.Model):
    """Track review history of procedures"""
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name='reviews')
    review_date = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    comments = models.TextField(blank=True)
    changes_required = models.BooleanField(default=False)
    approved = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-review_date']
    
    def __str__(self):
        return f"Review of {self.procedure.title} on {self.review_date.strftime('%Y-%m-%d')}"


class ProcedureAcknowledgment(models.Model):
    """Track crew acknowledgments of procedures"""
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name='acknowledgments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    acknowledged_date = models.DateTimeField(auto_now_add=True)
    acknowledged_version = models.CharField(max_length=20)
    comments = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['procedure', 'user', 'acknowledged_version']
        ordering = ['-acknowledged_date']
    
    def __str__(self):
        return f"{self.user.get_full_name()} acknowledged {self.procedure.title} v{self.acknowledged_version}"
