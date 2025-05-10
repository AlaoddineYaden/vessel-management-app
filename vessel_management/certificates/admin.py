# certificates/admin.py
from django.contrib import admin
from .models import Certificate, CertificateType, CertificateRenewal
from django.utils.html import format_html
from django.utils import timezone
@admin.register(CertificateType)
class CertificateTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_statutory', 'renewal_period_days')
    search_fields = ('name',)
    list_filter = ('is_statutory',)
    list_per_page = 20
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        'certificate_name', 'certificate_number', 'certificate_type', 
        'vessel_id', 'issue_date', 'colored_expiry_date', 'status'
    )
    list_filter = ('status', 'certificate_type', 'issuing_authority')
    search_fields = ('certificate_name', 'certificate_number', 'vessel_id')
    date_hierarchy = 'expiry_date'
    list_per_page = 20
    def colored_expiry_date(self, obj):
        today = timezone.now().date()
        days_to_expiry = (obj.expiry_date - today).days
        if days_to_expiry < 0:
            color = '#ffcdd2'  # red
        elif days_to_expiry <= 7:
            color = '#ffe0b2'  # orange
        elif days_to_expiry <= 30:
            color = '#fff9c4'  # yellow
        else:
            color = 'inherit'
        return format_html(
            '<div style="background-color: {}; padding: 4px;">{}</div>',
            color,
            obj.expiry_date.strftime('%b %d, %Y')
        )
    colored_expiry_date.short_description = 'Expiry date'
    colored_expiry_date.admin_order_field = 'expiry_date'
@admin.register(CertificateRenewal)
class CertificateRenewalAdmin(admin.ModelAdmin):
    list_display = ('certificate', 'status', 'initiated_date', 'due_date', 'completed_date')
    list_filter = ('status',)
    search_fields = ('certificate__certificate_name', 'certificate__certificate_number')
    date_hierarchy = 'due_date'
    list_per_page = 20