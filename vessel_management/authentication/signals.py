from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile
from utils.email_service import send_welcome_email

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update user profile when user is created or updated
    """
    if created:
        UserProfile.objects.create(user=instance)
        # Send welcome email to new users
        send_welcome_email(instance)
    else:
        # Make sure the user has a profile
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance) 