from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        CREW_MEMBER = 'CREW', _('Crew Member')
        FLEET_MANAGER = 'FLEET', _('Fleet Manager')
    
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=5, choices=Role.choices, default=Role.CREW_MEMBER)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Required for JWT authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Crew specific fields
    position = models.CharField(max_length=100, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"Profile of {self.user.email}"