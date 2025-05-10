from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .models import UserProfile
from utils.email_service import send_welcome_email

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update user profile when user is created or updated
    """
    try:
        if created:
            # Set is_staff to True for all new users
            instance.is_staff = True
            instance.save()
            
            # Check if profile already exists
            if not hasattr(instance, 'profile'):
                UserProfile.objects.create(user=instance)
            # Send welcome email to new users
            send_welcome_email(instance)
        else:
            # Make sure the user has a profile
            if not hasattr(instance, 'profile'):
                UserProfile.objects.get_or_create(user=instance)
    except IntegrityError:
        # If there's an integrity error, try to get the existing profile
        UserProfile.objects.get_or_create(user=instance)
    except Exception as e:
        # Log the error but don't prevent user creation
        print(f"Error creating user profile: {str(e)}") 