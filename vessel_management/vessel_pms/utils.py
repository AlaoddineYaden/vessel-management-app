from django.utils import timezone
from datetime import timedelta

def calculate_due_date(last_completed, interval_type, interval_value):
    """
    Calculate the next due date based on the last completed date and interval
    """
    if not last_completed:
        return timezone.now()
    
    if interval_type == 'daily':
        return last_completed + timedelta(days=interval_value)
    elif interval_type == 'weekly':
        return last_completed + timedelta(weeks=interval_value)
    elif interval_type == 'monthly':
        # Approximate months as 30 days
        return last_completed + timedelta(days=30 * interval_value)
    elif interval_type == 'quarterly':
        # Approximate quarters as 90 days
        return last_completed + timedelta(days=90 * interval_value)
    elif interval_type == 'semi_annual':
        # Approximate semi-annual as 180 days
        return last_completed + timedelta(days=180 * interval_value)
    elif interval_type == 'annual':
        # Approximate annual as 365 days
        return last_completed + timedelta(days=365 * interval_value)
    elif interval_type == 'custom_days':
        return last_completed + timedelta(days=interval_value)
    
    # Default case
    return last_completed + timedelta(days=interval_value)


def generate_notifications():
    """
    Generate notifications for tasks that are due soon or overdue
    Returns list of notification objects
    """
    from .models import MaintenanceTask
    
    now = timezone.now()
    soon = now + timedelta(days=7)
    
    # Get tasks due within the next 7 days
    due_soon_tasks = MaintenanceTask.objects.filter(
        next_due_date__gte=now,
        next_due_date__lte=soon,
        status__in=['scheduled', 'in_progress']
    )
    
    # Get overdue tasks
    overdue_tasks = MaintenanceTask.objects.filter(
        next_due_date__lt=now,
        status__in=['scheduled', 'in_progress']
    )
    
    # Update status of overdue tasks
    for task in overdue_tasks:
        if task.status != 'overdue':
            task.status = 'overdue'
            task.save()
    
    # Create notification objects
    notifications = []
    
    for task in due_soon_tasks:
        days_until = (task.next_due_date - now).days
        notifications.append({
            'task_id': task.id,
            'task_name': task.task_name,
            'equipment_id': task.equipment.id,
            'equipment_name': task.equipment.name,
            'due_date': task.next_due_date,
            'days_until_due': days_until,
            'type': 'due_soon',
            'message': f"Maintenance task '{task.task_name}' for '{task.equipment.name}' is due in {days_until} days"
        })
    
    for task in overdue_tasks:
        days_overdue = (now - task.next_due_date).days
        notifications.append({
            'task_id': task.id,
            'task_name': task.task_name,
            'equipment_id': task.equipment.id,
            'equipment_name': task.equipment.name,
            'due_date': task.next_due_date,
            'days_overdue': days_overdue,
            'type': 'overdue',
            'message': f"Maintenance task '{task.task_name}' for '{task.equipment.name}' is {days_overdue} days overdue"
        })
    
    return notifications