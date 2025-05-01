from django.contrib import admin
from .models import Vessel, SystemLog, File

@admin.register(Vessel)
class VesselAdmin(admin.ModelAdmin):
    list_display = ('name', 'imo_number', 'vessel_type', 'flag', 'build_year', 'is_active')
    list_filter = ('vessel_type', 'flag', 'build_year', 'is_active')
    search_fields = ('name', 'imo_number', 'mmsi_number', 'call_sign')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    list_per_page = 20

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('level', 'source', 'message', 'created_at', 'user')
    list_filter = ('level', 'source', 'created_at')
    search_fields = ('message', 'source')
    readonly_fields = ('level', 'message', 'source', 'created_at', 'user', 'ip_address')
    list_per_page = 20

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'file_type', 'content_type', 'file_size', 'created_at')
    list_filter = ('file_type', 'content_type', 'created_at')
    search_fields = ('file_name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    list_per_page = 20



