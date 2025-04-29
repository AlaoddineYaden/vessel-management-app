# notifications.py
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q
from .models import CorrectiveAction, PreventiveAction, NonConformity

def get_overdue_notifications():
    """
    Get notifications for overdue corrective actions
    """
    today = timezone.now().date()
    
    # Find actions that are overdue
    overdue_actions = CorrectiveAction.objects.filter(
        due_date__lt=today,
        completed_date__isnull=True
    )
    
    # Find actions that are due soon (in the next 7 days)
    due_soon_actions = CorrectiveAction.objects.filter(
        Q(due_date__gte=today) & 
        Q(due_date__lte=today + timezone.timedelta(days=7)),
        completed_date__isnull=True
    )
    
    notifications = []
    
    # Create notifications for overdue actions
    for action in overdue_actions:
        days_overdue = (today - action.due_date).days
        notifications.append({
            'type': 'overdue',
            'corrective_action_id': action.id,
            'non_conformity_id': action.non_conformity_id,
            'days_overdue': days_overdue,
            'assigned_to': action.assigned_to_id,
            'vessel_id': action.non_conformity.vessel_id,
            'message': f"Corrective action {action.id} is overdue by {days_overdue} days"
        })
    
    # Create notifications for actions due soon
    for action in due_soon_actions:
        days_remaining = (action.due_date - today).days
        notifications.append({
            'type': 'due_soon',
            'corrective_action_id': action.id,
            'non_conformity_id': action.non_conformity_id,
            'days_remaining': days_remaining,
            'assigned_to': action.assigned_to_id,
            'vessel_id': action.non_conformity.vessel_id,
            'message': f"Corrective action {action.id} is due in {days_remaining} days"
        })
    
    return notifications


def send_nonconformity_notification(nonconformity_id):
    """
    Send notification when a new non-conformity is created.
    """
    try:
        nonconformity = NonConformity.objects.get(id=nonconformity_id)
        
        # Get the vessel name (you might need to adjust this based on your model structure)
        vessel_name = f"Vessel ID: {nonconformity.vessel_id}"
        
        # Prepare email data
        subject = f"New Non-Conformity: {nonconformity.id}"
        context = {
            'nonconformity': nonconformity,
            'vessel_name': vessel_name,
            'severity': nonconformity.get_severity_display(),
            'source_type': nonconformity.get_source_type_display(),
            'detection_date': nonconformity.detection_date,
            'description': nonconformity.description,
        }
        
        # Render email templates
        html_message = render_to_string('nc_module/email/new_nonconformity.html', context)
        plain_message = render_to_string('nc_module/email/new_nonconformity.txt', context)
        
        # Send email to relevant users (you might need to adjust this based on your requirements)
        recipients = [user.email for user in settings.NOTIFICATION_RECIPIENTS]
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            html_message=html_message,
        )
        
        return True
    except NonConformity.DoesNotExist:
        return False


def send_action_assignment_notification(action_id, action_type='corrective'):
    """
    Send notification when a corrective or preventive action is assigned.
    """
    try:
        if action_type == 'corrective':
            action = CorrectiveAction.objects.get(id=action_id)
            action_model = CorrectiveAction
            action_type_display = 'Corrective Action'
        else:
            action = PreventiveAction.objects.get(id=action_id)
            action_model = PreventiveAction
            action_type_display = 'Preventive Action'
        
        # Get the non-conformity and vessel information
        nonconformity = action.non_conformity
        vessel_name = f"Vessel ID: {nonconformity.vessel_id}"
        
        # Prepare email data
        subject = f"New {action_type_display} Assigned: {action.id}"
        context = {
            'action': action,
            'action_type': action_type_display,
            'nonconformity': nonconformity,
            'vessel_name': vessel_name,
            'due_date': action.due_date,
            'description': action.description,
        }
        
        # Render email templates
        html_message = render_to_string('nc_module/email/action_assigned.html', context)
        plain_message = render_to_string('nc_module/email/action_assigned.txt', context)
        
        # Send email to the assigned user
        if action.assigned_to and action.assigned_to.email:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[action.assigned_to.email],
                html_message=html_message,
            )
            return True
        return False
    except (CorrectiveAction.DoesNotExist, PreventiveAction.DoesNotExist):
        return False


def send_action_due_reminder():
    """
    Send reminders for actions that are due soon.
    """
    today = timezone.now().date()
    
    # Get actions due in the next 3 days
    due_soon_corrective = CorrectiveAction.objects.filter(
        due_date__range=[today, today + timezone.timedelta(days=3)],
        completed_date__isnull=True
    )
    
    due_soon_preventive = PreventiveAction.objects.filter(
        due_date__range=[today, today + timezone.timedelta(days=3)],
        completed_date__isnull=True
    )
    
    # Send reminders for corrective actions
    for action in due_soon_corrective:
        if action.assigned_to and action.assigned_to.email:
            days_remaining = (action.due_date - today).days
            
            subject = f"Reminder: Corrective Action {action.id} Due in {days_remaining} days"
            context = {
                'action': action,
                'action_type': 'Corrective Action',
                'nonconformity': action.non_conformity,
                'days_remaining': days_remaining,
                'due_date': action.due_date,
            }
            
            html_message = render_to_string('nc_module/email/action_due_reminder.html', context)
            plain_message = render_to_string('nc_module/email/action_due_reminder.txt', context)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[action.assigned_to.email],
                html_message=html_message,
            )
    
    # Send reminders for preventive actions
    for action in due_soon_preventive:
        if action.assigned_to and action.assigned_to.email:
            days_remaining = (action.due_date - today).days
            
            subject = f"Reminder: Preventive Action {action.id} Due in {days_remaining} days"
            context = {
                'action': action,
                'action_type': 'Preventive Action',
                'nonconformity': action.non_conformity,
                'days_remaining': days_remaining,
                'due_date': action.due_date,
            }
            
            html_message = render_to_string('nc_module/email/action_due_reminder.html', context)
            plain_message = render_to_string('nc_module/email/action_due_reminder.txt', context)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[action.assigned_to.email],
                html_message=html_message,
            )
    
    return {
        'corrective_actions': due_soon_corrective.count(),
        'preventive_actions': due_soon_preventive.count()
    }

