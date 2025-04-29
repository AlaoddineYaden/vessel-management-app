# 13. utils/email_service.py
from django.conf import settings
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from sendgrid import SendGridAPIClient

def send_email(to_email, subject, content, from_email=None):
    """
    Generic function to send emails using SendGrid.
    """
    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=content
    )
    
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code
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
# 13. utils/email_service.py (continued)
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
