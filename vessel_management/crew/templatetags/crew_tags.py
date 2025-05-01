from django import template
from crew.models import CertificateNotification

register = template.Library()

@register.inclusion_tag('crew/notification_badge.html')
def certificate_notification_badge():
    """
    Template tag that returns the count of pending certificate notifications.
    """
    count = CertificateNotification.objects.filter(status='PENDING').count()
    return {'notification_count': count}

@register.inclusion_tag('crew/notification_list.html')
def certificate_notification_list():
    """
    Template tag that returns a list of pending certificate notifications.
    """
    notifications = CertificateNotification.objects.filter(
        status='PENDING'
    ).select_related(
        'certificate',
        'certificate__crew'
    ).order_by('-created_at')
    
    return {'notifications': notifications} 