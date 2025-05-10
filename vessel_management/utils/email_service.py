# 13. utils/email_service.py
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

def send_email(to_email, subject, content, from_email=None):
    """
    Generic function to send emails using Django's email backend.
    """
    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    try:
        # Convert HTML content to plain text for email clients that don't support HTML
        plain_message = strip_tags(content)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[to_email],
            html_message=content,
            fail_silently=False,
        )
        return 200  # Return success status code
    except Exception as e:
        # Log error
        from core.models import SystemLog
        SystemLog.objects.create(
            level=SystemLog.LogLevel.ERROR,
            message=f"Failed to send email: {str(e)}",
            source="email_service.py"
        )
        return None

def send_password_reset_email(to_email, token):
    """
    Send password reset email with reset link.
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    subject = "Password Reset Request"
    content = f"""
    <p>You have requested to reset your password.</p>
    <p>Please click the link below to reset your password:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>This link will expire in 24 hours.</p>
    <p>If you did not request a password reset, please ignore this email.</p>
    """
    
    return send_email(to_email, subject, content)

def send_welcome_email(user):
    """
    Send welcome email to newly registered users.
    """
    subject = "Welcome to Vessel Management System"
    content = f"""
    <p>Hello {user.first_name},</p>
    <p>Welcome to the Vessel Management System!</p>
    <p>Your account has been created successfully with the following details:</p>
    <ul>
        <li>Username: {user.username}</li>
        <li>Email: {user.email}</li>
        <li>Role: {user.get_role_display()}</li>
    </ul>
    <p>You can now log in to the system using your email and password.</p>
    <p>Thank you for joining us!</p>
    """
    
    return send_email(user.email, subject, content)

def send_password_change_notification(user):
    """
    Send notification email when user changes their password.
    """
    subject = "Password Changed Successfully"
    content = f"""
    <p>Hello {user.first_name},</p>
    <p>Your password has been successfully changed.</p>
    <p>If you did not make this change, please contact the system administrator immediately.</p>
    <p>Time of change: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """
    
    return send_email(user.email, subject, content)
