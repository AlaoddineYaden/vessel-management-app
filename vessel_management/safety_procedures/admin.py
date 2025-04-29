from django.contrib import admin
from .models import (
    ProcedureCategory,
    Procedure,
    ProcedureVersion,
    ProcedureReview,
    ProcedureAcknowledgment
)


class ProcedureCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent', 'order']
    list_filter = ['parent']
    search_fields = ['name', 'code', 'description']
    ordering = ['order', 'code']


class ProcedureVersionInline(admin.TabularInline):
    model = ProcedureVersion
    extra = 0
    readonly_fields = ['created_date']
    fields = ['version', 'created_by', 'created_date', 'change_notes']
    fk_name = 'procedure'


class ProcedureReviewInline(admin.TabularInline):
    model = ProcedureReview
    extra = 0
    readonly_fields = ['review_date']
    fields = ['reviewed_by', 'review_date', 'approved', 'changes_required', 'comments']


class ProcedureAcknowledgmentInline(admin.TabularInline):
    model = ProcedureAcknowledgment
    extra = 0
    readonly_fields = ['acknowledged_date']
    fields = ['user', 'acknowledged_date', 'acknowledged_version', 'comments']


class ProcedureAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'document_type', 
        'category', 
        'version', 
        'review_status', 
        'last_reviewed_date',
        'next_review_date',
        'is_active'
    ]
    list_filter = ['document_type', 'category', 'review_status', 'is_active']
    search_fields = ['title', 'content', 'tags']
    readonly_fields = ['created_date', 'review_status']
    fieldsets = [
        (None, {
            'fields': ['title', 'document_type', 'category', 'content', 'file_upload']
        }),
        ('Version Information', {
            'fields': ['version', 'created_date', 'created_by']
        }),
        ('Review Information', {
            'fields': ['last_reviewed_date', 'next_review_date', 'review_status', 'review_interval_months']
        }),
        ('Additional Information', {
            'fields': ['is_active', 'tags']
        }),
    ]
    inlines = [ProcedureVersionInline, ProcedureReviewInline, ProcedureAcknowledgmentInline]


class ProcedureVersionAdmin(admin.ModelAdmin):
    list_display = ['procedure', 'version', 'created_by', 'created_date']
    list_filter = ['created_by']
    search_fields = ['procedure__title', 'version', 'change_notes']
    readonly_fields = ['created_date']


class ProcedureReviewAdmin(admin.ModelAdmin):
    list_display = ['procedure', 'reviewed_by', 'review_date', 'approved', 'changes_required']
    list_filter = ['approved', 'changes_required', 'reviewed_by']
    search_fields = ['procedure__title', 'comments']
    readonly_fields = ['review_date']


class ProcedureAcknowledgmentAdmin(admin.ModelAdmin):
    list_display = ['procedure', 'user', 'acknowledged_date', 'acknowledged_version']
    list_filter = ['user', 'acknowledged_version']
    search_fields = ['procedure__title', 'comments']
    readonly_fields = ['acknowledged_date']


# Register models with their respective admin classes
admin.site.register(ProcedureCategory, ProcedureCategoryAdmin)
admin.site.register(Procedure, ProcedureAdmin)
admin.site.register(ProcedureVersion, ProcedureVersionAdmin)
admin.site.register(ProcedureReview, ProcedureReviewAdmin)
admin.site.register(ProcedureAcknowledgment, ProcedureAcknowledgmentAdmin)