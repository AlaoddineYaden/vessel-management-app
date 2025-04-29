# certificates/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404

from .models import Certificate, CertificateType, CertificateRenewal
from .serializers import (
    CertificateSerializer, CertificateDetailSerializer, CertificateTypeSerializer, 
    CertificateRenewalSerializer, CertificateUploadSerializer
)

class CertificateTypeViewSet(viewsets.ModelViewSet):
    queryset = CertificateType.objects.all()
    serializer_class = CertificateTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

# certificates/views.py
# Update any references to vessel_id to use vessel instead

class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Update filterset_fields to use vessel instead of vessel_id
    filterset_fields = ['certificate_type', 'status', 'vessel', 'issuing_authority']
    search_fields = ['certificate_name', 'certificate_number', 'notes', 'vessel__name', 'vessel__imo_number']
    ordering_fields = ['expiry_date', 'issue_date', 'updated_at']
    
    # Other methods remain the same
    
    @action(detail=False, methods=['get'])
    def get_by_vessel(self, request):
        """Get all certificates for a specific vessel"""
        vessel_id = request.query_params.get('vessel_id')
        if not vessel_id:
            return Response({"error": "vessel_id parameter is required"}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
        # Update to use the vessel field
        queryset = Certificate.objects.filter(vessel_id=vessel_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    # Update the notifications method to use vessel relationship
    @action(detail=False, methods=['get'])
    def notifications(self, request):
        """Generate notifications for certificates requiring attention"""
        expiring_soon = Certificate.objects.filter(status='expiring_soon')
        expired = Certificate.objects.filter(status='expired')
        
        notifications = []
        
        for cert in expiring_soon:
            days_left = (cert.expiry_date - timezone.now().date()).days
            notifications.append({
                'id': cert.id,
                'certificate_name': cert.certificate_name,
                'certificate_number': cert.certificate_number,
                'vessel_id': cert.vessel.id,
                'vessel_name': cert.vessel.name,
                'vessel_imo': cert.vessel.imo_number,
                'type': 'expiring_soon',
                'days_left': days_left,
                'message': f"Certificate {cert.certificate_name} for vessel {cert.vessel.name} will expire in {days_left} days"
            })
            
        for cert in expired:
            days_overdue = (timezone.now().date() - cert.expiry_date).days
            notifications.append({
                'id': cert.id,
                'certificate_name': cert.certificate_name,
                'certificate_number': cert.certificate_number,
                'vessel_id': cert.vessel.id,
                'vessel_name': cert.vessel.name,
                'vessel_imo': cert.vessel.imo_number,
                'type': 'expired',
                'days_overdue': days_overdue,
                'message': f"Certificate {cert.certificate_name} for vessel {cert.vessel.name} expired {days_overdue} days ago"
            })
            
        return Response(notifications)
    
    
class CertificateRenewalViewSet(viewsets.ModelViewSet):
    queryset = CertificateRenewal.objects.all()
    serializer_class = CertificateRenewalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'certificate']
    ordering_fields = ['due_date', 'initiated_date']
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending renewals"""
        queryset = CertificateRenewal.objects.filter(status='pending')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue renewals"""
        queryset = CertificateRenewal.objects.filter(status='overdue')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_in_progress(self, request, pk=None):
        """Mark a renewal as in progress"""
        renewal = self.get_object()
        renewal.status = 'in_progress'
        renewal.save()
        serializer = self.get_serializer(renewal)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a renewal as completed and update the certificate"""
        renewal = self.get_object()
        certificate = renewal.certificate
        
        # Get new certificate data from request
        new_issue_date = request.data.get('issue_date')
        new_expiry_date = request.data.get('expiry_date')
        new_certificate_number = request.data.get('certificate_number', certificate.certificate_number)
        
        if not new_issue_date or not new_expiry_date:
            return Response(
                {"error": "issue_date and expiry_date are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Update the certificate with new details
        certificate.issue_date = new_issue_date
        certificate.expiry_date = new_expiry_date
        certificate.certificate_number = new_certificate_number
        certificate.status = 'active'
        certificate.save()
        
        # Update the renewal
        renewal.status = 'completed'
        renewal.completed_date = timezone.now().date()
        renewal.save()
        
        serializer = self.get_serializer(renewal)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_notes(self, request, pk=None):
        """Add notes to a renewal"""
        renewal = self.get_object()
        notes = request.data.get('notes')
        
        if notes:
            if renewal.notes:
                renewal.notes += f"\n{timezone.now().strftime('%Y-%m-%d %H:%M')} - {notes}"
            else:
                renewal.notes = f"{timezone.now().strftime('%Y-%m-%d %H:%M')} - {notes}"
            
            renewal.save()
            serializer = self.get_serializer(renewal)
            return Response(serializer.data)
        
        return Response(
            {"error": "Notes field is required"},
            status=status.HTTP_400_BAD_REQUEST
        )