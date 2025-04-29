# audit_inspection/admin.py

from django.contrib import admin
from .models import (
    AuditType, Audit, AuditFinding, InspectionItem, 
    InspectionChecklist, Inspection, InspectionResult,
    AuditNotification, Vessel
)

@admin.register(Vessel)
class VesselAdmin(admin.ModelAdmin):
    list_display = ('name', 'imo_number')
    search_fields = ('name', 'imo_number')

@admin.register(AuditType)
class AuditTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'frequency_days', 'is_mandatory')
    list_filter = ('is_mandatory',)
    search_fields = ('name', 'description')

@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ('id', 'audit_type', 'vessel', 'planned_date', 'status', 'auditor')
    list_filter = ('status', 'audit_type')
    search_fields = ('vessel__name', 'comments')
    date_hierarchy = 'planned_date'

@admin.register(AuditFinding)
class AuditFindingAdmin(admin.ModelAdmin):
    list_display = ('id', 'audit', 'severity', 'status', 'due_date', 'assigned_to')
    list_filter = ('severity', 'status')
    search_fields = ('description', 'corrective_action')
    date_hierarchy = 'due_date'

@admin.register(InspectionItem)
class InspectionItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_mandatory')
    list_filter = ('category', 'is_mandatory')
    search_fields = ('name', 'description', 'regulation_reference')

@admin.register(InspectionChecklist)
class InspectionChecklistAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    filter_horizontal = ('items',)

@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'checklist', 'vessel', 'planned_date', 'status', 'inspector')
    list_filter = ('status', 'checklist')
    search_fields = ('vessel__name', 'comments')
    date_hierarchy = 'planned_date'

@admin.register(InspectionResult)
class InspectionResultAdmin(admin.ModelAdmin):
    list_display = ('inspection', 'item', 'result')
    list_filter = ('result',)
    search_fields = ('comments', 'item__name')

@admin.register(AuditNotification)
class AuditNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'notification_type', 'is_sent', 'created_at')
    list_filter = ('notification_type', 'is_sent')
    search_fields = ('message',)
    date_hierarchy = 'created_at'
    filter_horizontal = ('recipients',)
