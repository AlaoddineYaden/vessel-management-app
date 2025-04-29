import django_filters
from .models import ISMRequirement, ComplianceItem, ComplianceReview


class ISMRequirementFilter(django_filters.FilterSet):
    ism_section = django_filters.CharFilter(lookup_expr='exact')
    requirement_code = django_filters.CharFilter(lookup_expr='icontains')
    requirement_text = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = ISMRequirement
        fields = ['ism_section', 'requirement_code', 'requirement_text']


class ComplianceItemFilter(django_filters.FilterSet):
    ism_requirement = django_filters.UUIDFilter()
    vessel_id = django_filters.UUIDFilter()
    compliance_status = django_filters.MultipleChoiceFilter(choices=ComplianceItem.STATUS_CHOICES)
    risk_level = django_filters.MultipleChoiceFilter(choices=ComplianceItem.RISK_LEVEL_CHOICES)
    assessment_date_after = django_filters.DateTimeFilter(field_name='assessment_date', lookup_expr='gte')
    assessment_date_before = django_filters.DateTimeFilter(field_name='assessment_date', lookup_expr='lte')
    ism_section = django_filters.CharFilter(field_name='ism_requirement__ism_section')
    
    class Meta:
        model = ComplianceItem
        fields = ['ism_requirement', 'vessel_id', 'compliance_status', 'risk_level']


class ComplianceReviewFilter(django_filters.FilterSet):
    compliance_item = django_filters.UUIDFilter()
    status = django_filters.MultipleChoiceFilter(choices=ComplianceReview.REVIEW_STATUS_CHOICES)
    scheduled_date_after = django_filters.DateTimeFilter(field_name='scheduled_date', lookup_expr='gte')
    scheduled_date_before = django_filters.DateTimeFilter(field_name='scheduled_date', lookup_expr='lte')
    
    class Meta:
        model = ComplianceReview
        fields = ['compliance_item', 'status', 'reviewer']

