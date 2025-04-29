from django.utils import timezone
from .models import MaintenanceTask


def update_overdue_tasks():
    """
    Update task statuses based on due dates
    Should be run daily via a scheduler (e.g., Celery)
    """
    now = timezone.now()
    
    # Find tasks that are past their due date but not marked as overdue
    overdue_tasks = MaintenanceTask.objects.filter(
        next_due_date__lt=now,
        status__in=['scheduled', 'in_progress']
    )
    
    # Update their status
    updated_count = 0
    for task in overdue_tasks:
        task.status = 'overdue'
        task.save(update_fields=['status'])
        updated_count += 1
    
    return updated_count


def generate_recurring_tasks():
    """
    Generate new tasks for recurring maintenance
    Should be run daily via a scheduler (e.g., Celery)
    """
    # Find completed tasks with recurring schedule
    completed_tasks = MaintenanceTask.objects.filter(
        status='completed',
        interval_type__in=['daily', 'weekly', 'monthly', 'quarterly', 'semi_annual', 'annual', 'custom_days']
    )
    
    created_count = 0
    for completed_task in completed_tasks:
        # Calculate the next due date
        next_due = completed_task.calculate_next_due_date()
        
        # Update the task for the next cycle
        completed_task.status = 'scheduled'
        completed_task.next_due_date = next_due
        completed_task.save(update_fields=['status', 'next_due_date'])
        created_count += 1
    
    return created_count