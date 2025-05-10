# crew/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from .models import CrewCertificate, CertificateNotification, Crew
from utils.email_service import send_email
import random
import string

User = get_user_model()

def generate_crew_password(crew):
    """
    Generate a password using crew member's information
    Format: First letter of name + Last 4 digits of passport + Random 3 letters
    Example: J1234ABC
    """
    first_letter = crew.name[0].upper()
    passport_digits = ''.join(filter(str.isdigit, crew.passport_number))[-4:]
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    return f"{first_letter}{passport_digits}{random_letters}"

@receiver(post_save, sender=Crew)
def assign_crew_to_group(sender, instance, created, **kwargs):
    """
    When a crew member is created or updated, automatically assign them to the group
    corresponding to their rank.
    """
    if kwargs.get('raw', False):
        return  # Skip for raw saves

    # Map of ranks to group names
    rank_to_group = {
        'FLEET MANAGER': 'Fleet Manager',
        'CHIEF ENGINEER': 'Chief Engineer',
        'SECOND ENGINEER': 'Second Engineer',
        'CHIEF OFFICER': 'Chief Officer',
        'SECOND OFFICER': 'Second Officer',
        'THIRD OFFICER': 'Third Officer',
        'CAPTAIN': 'Captain',
        'DECK CREW': 'Deck Crew',
        'ENGINE CREW': 'Engine Crew',
    }

    # Get the group name for the crew member's rank
    group_name = rank_to_group.get(instance.rank.upper())
    if not group_name:
        return  # Skip if rank doesn't map to a group

    # Get the group
    group = Group.objects.get(name=group_name)

    # Remove the crew member from all groups first
    instance.user.groups.clear()

    # Add the crew member to the appropriate group
    instance.user.groups.add(group)

@receiver(post_save, sender=CrewCertificate)
def check_certificate_expiry(sender, instance, created, **kwargs):
    """
    When a certificate is created or updated, check if it's close to expiry
    and create a single notification at the appropriate threshold.
    """
    if kwargs.get('raw', False):
        return  # Skip for raw saves
    
    today = timezone.now().date()
    days_until_expiry = (instance.expiry_date - today).days
    
    # Delete any existing notifications for this certificate
    CertificateNotification.objects.filter(certificate=instance).delete()
    
    # Handle expired certificates
    if days_until_expiry < 0:
        message = f"Certificate '{instance.certificate_name}' for {instance.crew.name} has expired {abs(days_until_expiry)} days ago."
        CertificateNotification.objects.create(
            certificate=instance,
            days_before_expiry=0,
            message=message,
            sent_to=instance.crew.email
        )
        return
    
    # Determine which threshold we're at (90, 60, or 30 days)
    threshold = None
    if 0 <= days_until_expiry <= 30:
        threshold = 30
    elif 31 <= days_until_expiry <= 60:
        threshold = 60
    elif 61 <= days_until_expiry <= 90:
        threshold = 90
    
    if threshold is not None:
        # Create a new notification for the current threshold
        message = f"Certificate '{instance.certificate_name}' for {instance.crew.name} will expire in {days_until_expiry} days on {instance.expiry_date}."
        CertificateNotification.objects.create(
            certificate=instance,
            days_before_expiry=threshold,
            message=message,
            sent_to=instance.crew.email
        )

@receiver(post_save, sender=Crew)
def create_crew_user_account(sender, instance, created, **kwargs):
    """
    When a crew member is created, automatically create a user account and send credentials
    """
    if not created or kwargs.get('raw', False):
        return

    # Generate a password using crew member's information
    password = generate_crew_password(instance)
    
    try:
        # Create user account
        user = User.objects.create_user(
            username=instance.email,
            email=instance.email,
            password=password,
            first_name=instance.name.split()[0],
            last_name=' '.join(instance.name.split()[1:]) if len(instance.name.split()) > 1 else '',
            role=User.Role.CREW_MEMBER
        )
        
        # Send email with credentials
        subject = "Your Vessel Management System Account"
        content = f"""
        <p>Hello {instance.name},</p>
        <p>Your account has been created in the Vessel Management System.</p>
        <p>Here are your login credentials:</p>
        <ul>
            <li><strong>Email:</strong> {instance.email}</li>
            <li><strong>Password:</strong> {password}</li>
        </ul>
        <p>Your password is generated using your information for easy remembrance:</p>
        <ul>
            <li>First letter of your name</li>
            <li>Last 4 digits of your passport number</li>
            <li>3 random letters</li>
        </ul>
        <p>Please log in and change your password immediately for security reasons.</p>
        <p>Best regards,<br>Vessel Management Team</p>
        """
        
        send_email(instance.email, subject, content)
        
    except Exception as e:
        # Log the error but don't prevent crew member creation
        print(f"Error creating user account for crew member {instance.name}: {str(e)}")