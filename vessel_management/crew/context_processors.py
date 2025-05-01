from crew.models import CertificateNotification

def certificate_notifications(request):
    """
    Context processor that adds certificate notifications to the template context.
    """
    if not request.user.is_authenticated:
        return {}
    
    # Get all pending notifications
    notifications = CertificateNotification.objects.filter(
        status='PENDING'
    ).select_related(
        'certificate',
        'certificate__crew'
    ).order_by('-created_at')
    
    # Count notifications by type
    expired_count = notifications.filter(days_before_expiry=0).count()
    expiring_count = notifications.filter(days_before_expiry__gt=0).count()
    
    return {
        'certificate_notifications': notifications,
        'expired_certificate_count': expired_count,
        'expiring_certificate_count': expiring_count,
        'total_certificate_notifications': notifications.count(),
    } 