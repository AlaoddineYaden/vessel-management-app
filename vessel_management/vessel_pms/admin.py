from django.contrib import admin
from .models import Equipment, MaintenanceTask, MaintenanceHistory

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'serial_number', 'manufacturer', 'status', 'location')
    list_filter = ('status', 'manufacturer', 'location')
    search_fields = ('name', 'model', 'serial_number')
    date_hierarchy = 'installation_date'
    list_per_page = 20


@admin.register(MaintenanceTask)
class MaintenanceTaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'equipment', 'status', 'next_due_date', 'interval_type', 'responsible_role')
    list_filter = ('status', 'interval_type', 'responsible_role')
    search_fields = ('task_name', 'equipment__name', 'description')
    date_hierarchy = 'next_due_date'
    list_per_page = 20


@admin.register(MaintenanceHistory)
class MaintenanceHistoryAdmin(admin.ModelAdmin):
    list_display = ('task', 'equipment', 'completed_date', 'completed_by')
    list_filter = ('completed_date', 'equipment')
    search_fields = ('task__task_name', 'equipment__name', 'remarks')
    date_hierarchy = 'completed_date'
    list_per_page = 20