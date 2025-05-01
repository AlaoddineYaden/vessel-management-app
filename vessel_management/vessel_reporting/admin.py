from django.contrib import admin
from .models import Report, SavedReport, ReportSchedule, DashboardMetric


class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'created_by', 'created_date', 'is_public')
    list_filter = ('report_type', 'is_public', 'created_date')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_date'
    list_per_page = 20


class SavedReportAdmin(admin.ModelAdmin):
    list_display = ('report', 'file_format', 'generated_by', 'generated_date')
    list_filter = ('file_format', 'generated_date', 'report__report_type')
    search_fields = ('report__name',)
    date_hierarchy = 'generated_date'
    list_per_page = 20


class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'report', 'frequency', 'is_active', 'last_run')
    list_filter = ('frequency', 'is_active', 'output_format')
    search_fields = ('name', 'report__name')
    date_hierarchy = 'created_date'
    list_per_page = 20


class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ('name', 'metric_type', 'display_order', 'is_active', 'refresh_interval_minutes')
    list_filter = ('metric_type', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('display_order', 'is_active', 'refresh_interval_minutes')
    list_per_page = 20


admin.site.register(Report, ReportAdmin)
admin.site.register(SavedReport, SavedReportAdmin)
admin.site.register(ReportSchedule, ReportScheduleAdmin)
admin.site.register(DashboardMetric, DashboardMetricAdmin) 