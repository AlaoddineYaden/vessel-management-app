from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from core.models import Vessel

class Equipment(models.Model):
    """Model for vessel equipment that requires maintenance"""
    STATUS_CHOICES = (
        ('operational', 'Operational'),
        ('maintenance', 'Under Maintenance'),
        ('faulty', 'Faulty'),
        ('decommissioned', 'Decommissioned'),
    )
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    manufacturer = models.CharField(max_length=100)
    installation_date = models.DateField()
    location = models.CharField(max_length=100)
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, related_name='equipment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='operational')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.serial_number})"
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipment'


class MaintenanceTask(models.Model):
    """Model for maintenance tasks associated with equipment"""
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )
    
    INTERVAL_TYPE_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual'),
        ('running_hours', 'Running Hours'),
        ('custom_days', 'Custom Days'),
    )
    
    id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=100)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_tasks')
    description = models.TextField()
    interval_type = models.CharField(max_length=20, choices=INTERVAL_TYPE_CHOICES)
    interval_value = models.PositiveIntegerField(help_text="Value for interval (days or hours)")
    last_completed_date = models.DateTimeField(null=True, blank=True)
    next_due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    responsible_role = models.CharField(max_length=100)
    instructions = models.TextField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.task_name} - {self.equipment}"
    
    def calculate_next_due_date(self):
        """Calculate the next due date based on interval settings"""
        if not self.last_completed_date:
            return self.next_due_date
        
        if self.interval_type == 'daily':
            return self.last_completed_date + timedelta(days=1 * self.interval_value)
        elif self.interval_type == 'weekly':
            return self.last_completed_date + timedelta(weeks=1 * self.interval_value)
        elif self.interval_type == 'monthly':
            return self.last_completed_date + relativedelta(months=1 * self.interval_value)
        elif self.interval_type == 'quarterly':
            return self.last_completed_date + relativedelta(months=3 * self.interval_value)
        elif self.interval_type == 'semi_annual':
            return self.last_completed_date + relativedelta(months=6 * self.interval_value)
        elif self.interval_type == 'annual':
            return self.last_completed_date + relativedelta(years=1 * self.interval_value)
        elif self.interval_type == 'custom_days':
            return self.last_completed_date + timedelta(days=self.interval_value)
        # For running_hours, we'll need external data about equipment usage
        return self.next_due_date
    
    def is_overdue(self):
        """Check if the task is overdue"""
        return self.next_due_date < timezone.now() and self.status not in ['completed', 'cancelled']
    
    def days_until_due(self):
        """Calculate days until this maintenance is due"""
        if self.next_due_date:
            delta = self.next_due_date - timezone.now()
            return delta.days
        return None
    
    class Meta:
        ordering = ['next_due_date']
        verbose_name = 'Maintenance Task'
        verbose_name_plural = 'Maintenance Tasks'


class MaintenanceHistory(models.Model):
    """Model for tracking maintenance history"""
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(MaintenanceTask, on_delete=models.CASCADE, related_name='history')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_history')
    completed_date = models.DateTimeField(default=timezone.now)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='completed_maintenance'
    )
    remarks = models.TextField(blank=True)
    running_hours = models.PositiveIntegerField(null=True, blank=True, 
                                               help_text="Equipment running hours at time of maintenance")
    parts_used = models.TextField(blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.task} - {self.completed_date}"
    
    class Meta:
        ordering = ['-completed_date']
        verbose_name = 'Maintenance History'
        verbose_name_plural = 'Maintenance History'