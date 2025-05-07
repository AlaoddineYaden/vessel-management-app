from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from .models import NonConformity, CorrectiveAction, EvidenceFile, PreventiveAction, NCAttachment, NCComment, NCHistory


class EvidenceFileInline(admin.TabularInline):
    model = EvidenceFile
    extra = 1
    readonly_fields = ['created_by', 'created_at', 'file_preview']
    fields = ['file', 'file_preview', 'created_by', 'created_at']
    
    def file_preview(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">View File</a>', obj.file.url)
        return "-"
    file_preview.short_description = "Preview"


class CorrectiveActionInline(admin.TabularInline):
    model = CorrectiveAction
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class PreventiveActionInline(admin.TabularInline):
    model = PreventiveAction
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class NCAttachmentInline(admin.TabularInline):
    model = NCAttachment
    extra = 0
    readonly_fields = ['created_at']


class NCCommentInline(admin.TabularInline):
    model = NCComment
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class NCHistoryInline(admin.TabularInline):
    model = NCHistory
    extra = 0
    readonly_fields = ['created_at']
    can_delete = False


@admin.register(NonConformity)
class NonConformityAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'source_type', 'severity', 'vessel', 'status', 
        'detection_date', 'corrective_actions_count', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'source_type', 'severity', 'detection_date', 'vessel']
    search_fields = ['description', 'root_cause', 'id']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    date_hierarchy = 'detection_date'
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'description', 'detection_date', 'source_type', 'source_id', 
                'severity', 'vessel', 'status'
            ]
        }),
        ('Analysis', {
            'fields': ['root_cause', 'reference_documents']
        }),
        ('System Information', {
            'fields': ['created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    inlines = [CorrectiveActionInline, PreventiveActionInline]
    
    def corrective_actions_count(self, obj):
        count = obj.corrective_actions.count()
        url = reverse('admin:nc_module_correctiveaction_changelist') + f'?non_conformity__id__exact={obj.id}'
        return format_html('<a href="{}">{} action(s)</a>', url, count)
    corrective_actions_count.short_description = "Corrective Actions"
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CorrectiveAction)
class CorrectiveActionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'non_conformity_link', 'assigned_to', 'due_date', 
        'completed_date', 'verification_status', 'is_overdue'
    ]
    list_filter = ['verification_status', 'due_date', 'completed_date', 'assigned_to']
    search_fields = ['description', 'verification_comments']
    readonly_fields = ['created_at', 'updated_at']
    
    def non_conformity_link(self, obj):
        url = reverse('admin:nc_module_nonconformity_change', args=[obj.non_conformity.id])
        return format_html('<a href="{}">{}</a>', url, obj.non_conformity)
    non_conformity_link.short_description = "Non-Conformity"
    list_per_page = 20

@admin.register(EvidenceFile)
class EvidenceFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'corrective_action_link', 'file', 'created_by', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['file']
    readonly_fields = ['created_at']
    
    def corrective_action_link(self, obj):
        url = reverse('admin:nc_module_correctiveaction_change', args=[obj.corrective_action.id])
        return format_html('<a href="{}">{}</a>', url, obj.corrective_action)
    corrective_action_link.short_description = "Corrective Action"


@admin.register(PreventiveAction)
class PreventiveActionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'non_conformity_link', 'assigned_to', 'due_date', 
        'status', 'completed_date'
    ]
    list_filter = ['status', 'due_date', 'completed_date', 'assigned_to']
    search_fields = ['description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'due_date'
    
    def non_conformity_link(self, obj):
        url = reverse('admin:nc_module_nonconformity_change', args=[obj.non_conformity.id])
        return format_html('<a href="{}">{}</a>', url, obj.non_conformity)
    non_conformity_link.short_description = "Non-Conformity"


@admin.register(NCAttachment)
class NCAttachmentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'non_conformity', 'file_type', 'file_size', 'created_by', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['file_name', 'non_conformity__title']
    readonly_fields = ['created_at']


@admin.register(NCComment)
class NCCommentAdmin(admin.ModelAdmin):
    list_display = ['non_conformity', 'user', 'comment', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['comment', 'non_conformity__title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NCHistory)
class NCHistoryAdmin(admin.ModelAdmin):
    list_display = ['non_conformity', 'user', 'action', 'created_at']
    list_filter = ['action', 'user', 'created_at']
    search_fields = ['details', 'non_conformity__title', 'user__username']
    readonly_fields = ['created_at']
