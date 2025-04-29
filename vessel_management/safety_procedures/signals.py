# safety_procedures/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Procedure, ProcedureReview


@receiver(post_save, sender=Procedure)
def procedure_notification(sender, instance, created, **kwargs):
    """Send notifications when procedures are created or updated"""
    if not hasattr(settings, 'SAFETY_PROCEDURES_NOTIFICATION_EMAIL'):
        return
    
    notification_email = settings.SAFETY_PROCEDURES_NOTIFICATION_EMAIL
    
    if created:
        subject = f"New Safety Procedure Created: {instance.title}"
        message = (
            f"A new safety procedure has been created:\n\n"
            f"Title: {instance.title}\n"
            f"Type: {instance.get_document_type_display()}\n"
            f"Category: {instance.category}\n"
            f"Version: {instance.version}\n"
            f"Created by: {instance.created_by.get_full_name()}\n"
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [notification_email],
            fail_silently=True,
        )
    elif instance.review_status == 'OVERDUE':
        # Send notification for overdue procedures
        subject = f"OVERDUE Safety Procedure Review: {instance.title}"
        message = (
            f"The following safety procedure is overdue for review:\n\n"
            f"Title: {instance.title}\n"
            f"Type: {instance.get_document_type_display()}\n"
            f"Category: {instance.category}\n"
            f"Version: {instance.version}\n"
            f"Last Reviewed: {instance.last_reviewed_date.strftime('%Y-%m-%d') if instance.last_reviewed_date else 'Never'}\n"
            f"Review Due: {instance.next_review_date.strftime('%Y-%m-%d') if instance.next_review_date else 'Unknown'}\n"
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [notification_email],
            fail_silently=True,
        )


@receiver(post_save, sender=ProcedureReview)
def review_notification(sender, instance, created, **kwargs):
    """Send notifications when procedures are reviewed"""
    if not created or not hasattr(settings, 'SAFETY_PROCEDURES_NOTIFICATION_EMAIL'):
        return
    
    notification_email = settings.SAFETY_PROCEDURES_NOTIFICATION_EMAIL
    
    subject = f"Safety Procedure Reviewed: {instance.procedure.title}"
    status = "Approved" if instance.approved else "Requires Changes"
    
    message = (
        f"A safety procedure has been reviewed:\n\n"
        f"Title: {instance.procedure.title}\n"
        f"Version: {instance.procedure.version}\n"
        f"Reviewed By: {instance.reviewed_by.get_full_name()}\n"
        f"Review Date: {instance.review_date.strftime('%Y-%m-%d')}\n"
        f"Status: {status}\n"
        f"Comments: {instance.comments}\n"
    )
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [notification_email],
        fail_silently=True,
    )
