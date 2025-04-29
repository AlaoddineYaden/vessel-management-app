from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MaintenanceTask
from django.utils import timezone


@receiver(post_save, sender=MaintenanceTask)
def update_task_status(sender, instance, created, **kwargs):
    """
    Signal to automatically update task status based on due date
    """
    if created:
        # No need to change status for newly created tasks
        return
    
    # Check if task is overdue
    if instance.next_due_date < timezone.now() and instance.status not in ['completed', 'cancelled', 'overdue']:
        instance.status = 'overdue'
        # Use update to avoid triggering this signal again
        MaintenanceTask.objects.filter(pk=instance.pk).update(status='overdue')