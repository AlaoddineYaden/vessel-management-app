# certificates/filters.py
from django_filters import rest_framework as filters
from .models import Certificate, CertificateRenewal
from django.utils import timezone
from datetime import timedelta

class CertificateFilter(filters.FilterSet):
    expiry_date_from = filters.DateFilter(field_name="expiry_date", lookup_expr='gte')
    expiry_date_to = filters.DateFilter(field_name="expiry_date", lookup_expr='lte')
    issue_date_from = filters.DateFilter(field_name="issue_date", lookup_expr='gte')
    issue_date_to = filters.DateFilter(field_name="issue_date", lookup_expr='lte')
    days_to_expiry = filters.NumberFilter(method='filter_days_to_expiry')
    vessel_name = filters.CharFilter(field_name='vessel__name', lookup_expr='icontains')
    vessel_imo = filters.CharFilter(field_name='vessel__imo_number', lookup_expr='icontains')
    
    class Meta:
        model = Certificate
        fields = [
            'certificate_type', 'status', 'vessel', 'issuing_authority',
            'expiry_date_from', 'expiry_date_to', 'issue_date_from', 'issue_date_to',
            'vessel_name', 'vessel_imo'
        ]
        
    def filter_days_to_expiry(self, queryset, name, value):
        """Filter certificates by days to expiry"""
        today = timezone.now().date()
        target_date = today + timedelta(days=int(value))
        return queryset.filter(expiry_date__lte=target_date, expiry_date__gte=today)
    

class CertificateRenewalFilter(filters.FilterSet):
    due_date_from = filters.DateFilter(field_name="due_date", lookup_expr='gte')
    due_date_to = filters.DateFilter(field_name="due_date", lookup_expr='lte')
    
    class Meta:
        model = CertificateRenewal
        fields = ['status', 'certificate', 'due_date_from', 'due_date_to']