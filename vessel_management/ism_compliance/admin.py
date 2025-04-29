from django.contrib import admin
from .models import ISMRequirement, ComplianceItem, ComplianceEvidence, ComplianceReview


@admin.register(ISMRequirement)
class ISMRequirementAdmin(admin.ModelAdmin):
    list_display = ('requirement_code', 'ism_section', 'requirement_text')
    list_filter = ('ism_section',)
    search_fields = ('requirement_code', 'requirement_text')


@admin.register(ComplianceItem)
class ComplianceItemAdmin(admin.ModelAdmin):
    list_display = ('ism_requirement', 'vessel_id', 'compliance_status', 'risk_level', 'assessment_date')
    list_filter = ('compliance_status', 'risk_level', 'assessment_date')
    search_fields = ('vessel_id', 'comments')
    date_hierarchy = 'assessment_date'


@admin.register(ComplianceEvidence)
class ComplianceEvidenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'evidence_type', 'compliance_item', 'upload_date')
    list_filter = ('evidence_type', 'upload_date')
    search_fields = ('title', 'description')


@admin.register(ComplianceReview)
class ComplianceReviewAdmin(admin.ModelAdmin):
    list_display = ('compliance_item', 'scheduled_date', 'status', 'reviewer')
    list_filter = ('status', 'scheduled_date')
    date_hierarchy = 'scheduled_date'
