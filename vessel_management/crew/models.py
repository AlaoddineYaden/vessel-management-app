# crew/models.py
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.conf import settings
from core.models import BaseModel, Vessel


class Crew(models.Model):
    """
    Model representing crew members of vessels.
    """
    RANK_CHOICES = [
        ('CAPTAIN', 'Captain'),
        ('CHIEF_OFFICER', 'Chief Officer'),
        ('SECOND_OFFICER', 'Second Officer'),
        ('THIRD_OFFICER', 'Third Officer'),
        ('CHIEF_ENGINEER', 'Chief Engineer'),
        ('SECOND_ENGINEER', 'Second Engineer'),
        ('THIRD_ENGINEER', 'Third Engineer'),
        ('ELECTRICIAN', 'Electrician'),
        ('BOSUN', 'Bosun'),
        ('ABLE_SEAMAN', 'Able Seaman'),
        ('COOK', 'Cook'),
        ('STEWARD', 'Steward'),
        ('OILER', 'Oiler'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    rank = models.CharField(max_length=20, choices=RANK_CHOICES)
    nationality = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=20, unique=True)
    seaman_book_number = models.CharField(max_length=20, unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmailField()
    address = models.TextField()
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17)
    medical_information = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_rank_display()}"
    
    def get_active_certificates(self):
        """Returns all non-expired certificates for this crew member"""
        return self.certificates.filter(expiry_date__gt=timezone.now().date())
    
    def get_expired_certificates(self):
        """Returns all expired certificates for this crew member"""
        return self.certificates.filter(expiry_date__lte=timezone.now().date())
    
    def get_soon_to_expire_certificates(self, days=90):
        """Returns certificates that will expire in the next specified days"""
        today = timezone.now().date()
        max_date = today + timezone.timedelta(days=days)
        return self.certificates.filter(
            expiry_date__gt=today,
            expiry_date__lte=max_date
        )
    
    def is_fully_certified(self):
        """Check if crew member has all required certificates for their rank"""
        # This method would contain logic to check if the crew member has all
        # required certificates for their specific rank
        # Implementation would depend on specific maritime regulations
        return True  # Placeholder


class CrewCertificate(models.Model):
    """
    Model representing certificates held by crew members.
    """
    CERTIFICATE_TYPES = [
        ('COC', 'Certificate of Competency'),
        ('COE', 'Certificate of Endorsement'),
        ('STCW', 'STCW Certificate'),
        ('MEDICAL', 'Medical Certificate'),
        ('SAFETY', 'Safety Training Certificate'),
        ('SECURITY', 'Security Training Certificate'),
        ('OTHER', 'Other Certificate'),
    ]
    
    id = models.AutoField(primary_key=True)
    crew = models.ForeignKey(Crew, related_name='certificates', on_delete=models.CASCADE)
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPES)
    certificate_name = models.CharField(max_length=100)
    certificate_number = models.CharField(max_length=50)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    issuing_authority = models.CharField(max_length=100)
    document_file = models.FileField(upload_to='crew_certificates/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.certificate_name} - {self.crew.name}"
    
    def is_expired(self):
        """Check if certificate is expired"""
        return self.expiry_date < timezone.now().date()
    
    def days_until_expiry(self):
        """Calculate days remaining until certificate expires"""
        if self.is_expired():
            return -1 * (timezone.now().date() - self.expiry_date).days
        return (self.expiry_date - timezone.now().date()).days
    
    class Meta:
        unique_together = ('crew', 'certificate_type', 'certificate_number')


class CrewAssignment(models.Model):
    """
    Model tracking crew assignments to vessels.
    """
    id = models.AutoField(primary_key=True)
    crew = models.ForeignKey(Crew, related_name='assignments', on_delete=models.CASCADE)
    vessel = models.ForeignKey(Vessel, related_name='crew_assignments', on_delete=models.CASCADE)
    rank = models.CharField(max_length=20, choices=Crew.RANK_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['crew', 'vessel', 'start_date']
        ordering = ['-start_date']
    
    def __str__(self):
        end_info = f" to {self.end_date}" if self.end_date else " (current)"
        return f"{self.crew.name} - {self.vessel.name} - {self.get_rank_display()} - {self.start_date}{end_info}"
    
    def save(self, *args, **kwargs):
        # When setting an end date, automatically update is_current
        if self.end_date and self.end_date <= timezone.now().date():
            self.is_current = False
        super().save(*args, **kwargs)


class CertificateNotification(BaseModel):
    """
    Model for storing certificate expiry notifications.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Notification Sent'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('RESOLVED', 'Resolved'),
    ]
    
    certificate = models.ForeignKey(CrewCertificate, related_name='notifications', on_delete=models.CASCADE)
    notification_date = models.DateField(auto_now_add=True)
    days_before_expiry = models.IntegerField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    message = models.TextField()
    sent_to = models.EmailField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.certificate.certificate_name} - {self.certificate.crew.name}"