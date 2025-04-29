from django.db import models
from django.utils import timezone


class MaintenanceTaskManager(models.Manager):
    """Custom manager for MaintenanceTask model"""
    
    def overdue(self):
        """Get all overdue tasks"""
        return self.filter(next_due_date__lt=timezone.now(), status__in=['scheduled', 'in_progress'])
    
    def due_soon(self, days=7):
        """Get tasks due within specified days"""
        now = timezone.now()
        soon = now + timezone.timedelta(days=days)
        return self.filter(next_due_date__gte=now, next_due_date__lte=soon, status__in=['scheduled', 'in_progress'])
    
    def by_status(self, status):
        """Filter tasks by status"""
        return self.filter(status=status)
    
    def by_equipment(self, equipment_id):
        """Filter tasks by equipment"""
        return self.filter(equipment_id=equipment_id)


class MaintenanceHistoryManager(models.Manager):
    """Custom manager for MaintenanceHistory model"""
    
    def recent(self, days=30):
        """Get maintenance history from the last X days"""
        since = timezone.now() - timezone.timedelta(days=days)
        return self.filter(completed_date__gte=since)
    
    def by_equipment(self, equipment_id):
        """Get history for specific equipment"""
        return self.filter(equipment_id=equipment_id)
    
    def by_task(self, task_id):
        """Get history for specific task"""
        return self.filter(task_id=task_id)