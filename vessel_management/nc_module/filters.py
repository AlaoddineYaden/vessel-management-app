import django_filters
from django.utils import timezone
from .models import NonConformity, CorrectiveAction, PreventiveAction


class NonConformityFilter(django_filters.FilterSet):
    vessel_id = django_filters.NumberFilter(field_name='vessel_id')
    source_type = django_filters.ChoiceFilter(choices=NonConformity.SOURCE_CHOICES)
    severity = django_filters.ChoiceFilter(choices=NonConformity.SEVERITY_CHOICES)
    status = django_filters.ChoiceFilter(choices=NonConformity.STATUS_CHOICES)
    detection_date_after = django_filters.DateFilter(field_name='detection_date', lookup_expr='gte')
    detection_date_before = django_filters.DateFilter(field_name='detection_date', lookup_expr='lte')
    created_by = django_filters.NumberFilter(field_name='created_by')
    
    class Meta:
        model = NonConformity
        fields = ['vessel_id', 'source_type', 'severity', 'status', 'detection_date_after', 'detection_date_before', 'created_by']


class CorrectiveActionFilter(django_filters.FilterSet):
    non_conformity = django_filters.NumberFilter(field_name='non_conformity')
    assigned_to = django_filters.NumberFilter(field_name='assigned_to')
    verification_status = django_filters.ChoiceFilter(choices=CorrectiveAction.VERIFICATION_STATUS_CHOICES)
    due_date_after = django_filters.DateFilter(field_name='due_date', lookup_expr='gte')
    due_date_before = django_filters.DateFilter(field_name='due_date', lookup_expr='lte')
    is_overdue = django_filters.BooleanFilter(method='filter_is_overdue')
    
    def filter_is_overdue(self, queryset, name, value):
        today = timezone.now().date()
        if value:
            return queryset.filter(due_date__lt=today, completed_date__isnull=True)
        return queryset.exclude(due_date__lt=today, completed_date__isnull=True)
    
    class Meta:
        model = CorrectiveAction
        fields = ['non_conformity', 'assigned_to', 'verification_status', 'due_date_after', 'due_date_before', 'is_overdue']


class PreventiveActionFilter(django_filters.FilterSet):
    non_conformity = django_filters.NumberFilter(field_name='non_conformity')
    assigned_to = django_filters.NumberFilter(field_name='assigned_to')
    status = django_filters.ChoiceFilter(choices=PreventiveAction.STATUS_CHOICES)
    due_date_after = django_filters.DateFilter(field_name='due_date', lookup_expr='gte')
    due_date_before = django_filters.DateFilter(field_name='due_date', lookup_expr='lte')
    
    class Meta:
        model = PreventiveAction
        fields = ['non_conformity', 'assigned_to', 'status', 'due_date_after', 'due_date_before']

