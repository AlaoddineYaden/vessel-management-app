from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_certificate_notification_email(notification):
    """
    Send an email notification for a certificate expiry.
    """
    subject = f"Certificate Expiry Notification: {notification.certificate.certificate_name}"
    
    # Prepare context for the email template
    context = {
        'certificate': notification.certificate,
        'crew_member': notification.certificate.crew,
        'days_until_expiry': notification.days_before_expiry,
        'expiry_date': notification.certificate.expiry_date,
        'message': notification.message,
    }
    
    # Render HTML and plain text versions of the email
    html_message = render_to_string('crew/email/certificate_notification.html', context)
    plain_message = strip_tags(html_message)
    
    # Send the email
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[notification.sent_to],
        fail_silently=False,
    )
    
    # Update notification status
    notification.status = 'SENT'
    notification.save() 