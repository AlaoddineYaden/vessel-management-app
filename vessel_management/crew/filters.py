# crew/filters.py
import django_filters
from django.db.models import Q
from .models import Crew, CrewCertificate, CrewAssignment


class CrewFilter(django_filters.FilterSet):
    """Filter for Crew model"""
    name = django_filters.CharFilter(lookup_expr='icontains')
    nationality = django_filters.CharFilter(lookup_expr='icontains')
    rank = django_filters.CharFilter(lookup_expr='iexact')
    is_active = django_filters.BooleanFilter()
    has_certificate_type = django_filters.CharFilter(method='filter_by_certificate_type')
    has_valid_certificate = django_filters.CharFilter(method='filter_by_valid_certificate')
    
    def filter_by_certificate_type(self, queryset, name, value):
        return queryset.filter(certificates__certificate_type=value).distinct()
    
    def filter_by_valid_certificate(self, queryset, name, value):
        from django.utils import timezone
        today = timezone.now().date()
        return queryset.filter(
            certificates__certificate_type=value,
            certificates__expiry_date__gt=today
        ).distinct()
    
    class Meta:
        model = Crew
        fields = ['name', 'nationality', 'rank', 'is_active']


class CertificateFilter(django_filters.FilterSet):
    """Filter for CrewCertificate model"""
    certificate_name = django_filters.CharFilter(lookup_expr='icontains')
    certificate_type = django_filters.CharFilter(lookup_expr='iexact')
    issuing_authority = django_filters.CharFilter(lookup_expr='icontains')
    issue_date_from = django_filters.DateFilter(field_name='issue_date', lookup_expr='gte')
    issue_date_to = django_filters.DateFilter(field_name='issue_date', lookup_expr='lte')
    expiry_date_from = django_filters.DateFilter(field_name='expiry_date', lookup_expr='gte')
    expiry_date_to = django_filters.DateFilter(field_name='expiry_date', lookup_expr='lte')
    is_expired = django_filters.BooleanFilter(method='filter_by_expiry')
    
    def filter_by_expiry(self, queryset, name, value):
        from django.utils import timezone
        today = timezone.now().date()
        if value:  # True - get expired certificates
            return queryset.filter(expiry_date__lt=today)
        else:  # False - get valid certificates
            return queryset.filter(expiry_date__gte=today)
    
    class Meta:
        model = CrewCertificate
        fields = [
            'crew', 'certificate_type', 'certificate_name',
            'issuing_authority'
        ]


class AssignmentFilter(django_filters.FilterSet):
    """Filter for CrewAssignment model"""
    crew_name = django_filters.CharFilter(field_name='crew__name', lookup_expr='icontains')
    vessel_name = django_filters.CharFilter(field_name='vessel__name', lookup_expr='icontains')
    rank = django_filters.CharFilter(lookup_expr='iexact')
    is_current = django_filters.BooleanFilter()
    start_date_from = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    
    class Meta:
        model = CrewAssignment
        fields = ['crew', 'vessel', 'rank', 'is_current']