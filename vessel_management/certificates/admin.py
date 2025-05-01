# certificates/admin.py
from django.contrib import admin
from .models import Certificate, CertificateType, CertificateRenewal

@admin.register(CertificateType)
class CertificateTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_statutory', 'renewal_period_days')
    search_fields = ('name',)
    list_filter = ('is_statutory',)

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_name', 'certificate_number', 'certificate_type', 
                   'vessel_id', 'issue_date', 'expiry_date', 'status')
    list_filter = ('status', 'certificate_type', 'issuing_authority')
    search_fields = ('certificate_name', 'certificate_number', 'vessel_id')
    date_hierarchy = 'expiry_date'
    list_per_page = 20
@admin.register(CertificateRenewal)
class CertificateRenewalAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'status', 'initiated_date', 'due_date', 'completed_date')
    list_filter = ('status',)
    search_fields = ('certificate__certificate_name', 'certificate__certificate_number')
    date_hierarchy = 'due_date'