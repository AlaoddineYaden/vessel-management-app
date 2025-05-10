# crew/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import Crew, CrewCertificate, CrewAssignment, Vessel, CertificateNotification
from .utils import send_certificate_notification_email


class CrewCertificateInline(admin.TabularInline):
    model = CrewCertificate
    extra = 0
    fields = ('certificate_name', 'certificate_type', 'certificate_number', 
              'issue_date', 'expiry_date', 'issuing_authority', 'document_file')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('expiry_date')


class CrewAssignmentInline(admin.TabularInline):
    model = CrewAssignment
    extra = 0
    fields = ('vessel', 'rank', 'start_date', 'end_date', 'is_current')


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rank', 'nationality', 'is_active', 'certificate_status', 'current_vessel')
    list_filter = ('rank', 'nationality', 'is_active')
    search_fields = ('name', 'passport_number', 'seaman_book_number', 'email')
    inlines = [CrewCertificateInline, CrewAssignmentInline]
    
    def certificate_status(self, obj):
        expired = obj.get_expired_certificates().count()
        expiring_soon = obj.get_soon_to_expire_certificates(days=30).count()
        
        if expired > 0:
            return format_html(
                '<span style="color: red;">⚠️ {} expired</span>', expired
            )
        elif expiring_soon > 0:
            return format_html(
                '<span style="color: orange;">⚠️ {} expiring soon</span>', expiring_soon
            )
        return format_html('<span style="color: green;">✓ Valid</span>')
    
    certificate_status.short_description = "Certificates"
    
    def current_vessel(self, obj):
        current_assignment = obj.assignments.filter(is_current=True).first()
        if current_assignment:
            return current_assignment.vessel.name
        return "Not assigned"
    
    current_vessel.short_description = "Current Vessel"


@admin.register(CrewCertificate)
class CrewCertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_name', 'crew_name', 'certificate_type', 
                   'issue_date', 'colored_expiry_date', 'expiry_status')
    list_filter = ('certificate_type', 'issuing_authority')
    search_fields = ('certificate_name', 'certificate_number', 'crew__name')
    list_per_page = 20
    def crew_name(self, obj):
        return obj.crew.name
    crew_name.short_description = "Crew Member"
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
    
    def expiry_status(self, obj):
        today = timezone.now().date()
        if obj.expiry_date < today:
            days = (today - obj.expiry_date).days
            return format_html(
                '<span style="color: red;">Expired {} days ago</span>', days
            )
        
        days = (obj.expiry_date - today).days
        if days <= 30:
            return format_html(
                '<span style="color: orange;">Expires in {} days</span>', days
            )
        elif days <= 90:
            return format_html(
                '<span style="color: #CCCC00;">Expires in {} days</span>', days
            )
        return format_html(
            '<span style="color: green;">Valid for {} days</span>', days
        )
    
    expiry_status.short_description = "Expiry Status"


@admin.register(CrewAssignment)
class CrewAssignmentAdmin(admin.ModelAdmin):
    list_display = ('crew_name', 'vessel_name', 'rank', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'rank')
    search_fields = ('crew__name', 'vessel__name')
    
    def crew_name(self, obj):
        return obj.crew.name
    
    crew_name.short_description = "Crew Member"
    
    def vessel_name(self, obj):
        return obj.vessel.name
    
    vessel_name.short_description = "Vessel"


@admin.register(CertificateNotification)
class CertificateNotificationAdmin(admin.ModelAdmin):
    list_display = ('certificate_info', 'crew_name', 'notification_date', 'days_before_expiry', 'status', 'created_at', 'message_preview', 'send_email_button')
    list_filter = ('status', 'days_before_expiry', 'created_at', 'notification_date')
    search_fields = ('certificate__certificate_name', 'certificate__crew__name', 'message')
    list_per_page = 20
    date_hierarchy = 'created_at'
    actions = ['mark_as_sent', 'mark_as_resolved', 'mark_as_acknowledged', 'send_notification_emails']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:notification_id>/send-email/',
                self.admin_site.admin_view(self.send_notification_email),
                name='crew-certificatenotification-send-email',
            ),
        ]
        return custom_urls + urls
    
    def send_notification_email(self, request, notification_id):
        notification = CertificateNotification.objects.get(id=notification_id)
        try:
            send_certificate_notification_email(notification)
            messages.success(request, f'Email notification sent successfully to {notification.sent_to}')
        except Exception as e:
            messages.error(request, f'Failed to send email: {str(e)}')
        return redirect('admin:crew_certificatenotification_changelist')
    
    def send_email_button(self, obj):
        if obj.status != 'SENT' and obj.sent_to:
            return format_html(
                '<a class="button" href="{}">Send Email</a>',
                f'admin:crew-certificatenotification-send-email',
                obj.id
            )
        return format_html(
            '<span style="color: green;">✓ Sent</span>' if obj.status == 'SENT' else 
            '<span style="color: red;">No email address</span>'
        )
    send_email_button.short_description = 'Email Status'
    send_email_button.allow_tags = True
    
    def send_notification_emails(self, request, queryset):
        success_count = 0
        error_count = 0
        
        for notification in queryset:
            if notification.status != 'SENT' and notification.sent_to:
                try:
                    send_certificate_notification_email(notification)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    messages.error(request, f'Failed to send email to {notification.sent_to}: {str(e)}')
        
        if success_count:
            messages.success(request, f'Successfully sent {success_count} email notifications.')
        if error_count:
            messages.warning(request, f'Failed to send {error_count} email notifications.')
    send_notification_emails.short_description = "Send email notifications"
    
    def certificate_info(self, obj):
        return format_html(
            '<strong>{}</strong> ({})',
            obj.certificate.certificate_name,
            obj.certificate.certificate_type
        )
    certificate_info.short_description = "Certificate"
    certificate_info.admin_order_field = 'certificate__certificate_name'
    
    def crew_name(self, obj):
        return obj.certificate.crew.name
    crew_name.short_description = "Crew Member"
    crew_name.admin_order_field = 'certificate__crew__name'
    
    def message_preview(self, obj):
        return format_html(
            '<span title="{}">{}</span>',
            obj.message,
            obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
        )
    message_preview.short_description = "Message Preview"
    
    def mark_as_sent(self, request, queryset):
        queryset.update(status='SENT')
    mark_as_sent.short_description = "Mark selected notifications as sent"
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='RESOLVED')
    mark_as_resolved.short_description = "Mark selected notifications as resolved"
    
    def mark_as_acknowledged(self, request, queryset):
        queryset.update(status='ACKNOWLEDGED')
    mark_as_acknowledged.short_description = "Mark selected notifications as acknowledged"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'certificate',
            'certificate__crew'
        )