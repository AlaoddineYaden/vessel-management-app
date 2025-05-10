from django.contrib import admin
from .models import Equipment, MaintenanceTask, MaintenanceHistory
from django.utils.html import format_html
from django.utils import timezone

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'serial_number', 'manufacturer', 'status', 'location')
    list_filter = ('status', 'manufacturer', 'location')
    search_fields = ('name', 'model', 'serial_number')
    date_hierarchy = 'installation_date'
    list_per_page = 20


@admin.register(MaintenanceTask)
class MaintenanceTaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'equipment', 'status', 'colored_next_due_date', 'interval_type', 'responsible_role')
    list_filter = ('status', 'interval_type', 'responsible_role')
    search_fields = ('task_name', 'equipment__name', 'description')
    date_hierarchy = 'next_due_date'
    list_per_page = 20

    def colored_next_due_date(self, obj):
        today = timezone.now().date()
        due_date = obj.next_due_date.date() if hasattr(obj.next_due_date, 'date') else obj.next_due_date
        days_to_due = (due_date - today).days
        if obj.status == 'completed':
            color = '#c8e6c9'  # green
        elif obj.status == 'in_progress':
            color = '#bbdefb'  # light blue
        elif days_to_due < 0:
            color = '#ffcdd2'  # red
        elif days_to_due <= 7:
            color = '#ffe0b2'  # orange
        elif days_to_due <= 30:
            color = '#fff9c4'  # yellow
        else:
            color = 'inherit'
        return format_html(
            '<div style="background-color: {}; padding: 4px;">{}</div>',
            color,
            obj.next_due_date.strftime('%b %d, %Y')
        )
    colored_next_due_date.short_description = 'Next due date'
    colored_next_due_date.admin_order_field = 'next_due_date'


@admin.register(MaintenanceHistory)
class MaintenanceHistoryAdmin(admin.ModelAdmin):
    list_display = ('task', 'equipment', 'completed_date', 'completed_by')
    list_filter = ('completed_date', 'equipment')
    search_fields = ('task__task_name', 'equipment__name', 'remarks')
    date_hierarchy = 'completed_date'
    list_per_page = 20