# crew/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from .models import (
    Crew, CrewCertificate, CrewAssignment, 
    Vessel, CertificateNotification
)
from .serializers import (
    CrewSerializer, CrewDetailSerializer, CrewCertificateSerializer, 
    CrewAssignmentSerializer, VesselSerializer, CertificateNotificationSerializer
)
from .filters import CrewFilter, CertificateFilter, AssignmentFilter


class CrewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Crew members management.
    """
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CrewFilter
    search_fields = ['name', 'passport_number', 'seaman_book_number', 'nationality', 'rank']
    ordering_fields = ['name', 'rank', 'nationality', 'created_at', 'updated_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'crew_detail':
            return CrewDetailSerializer
        return CrewSerializer
    
    @action(detail=True, methods=['get'])
    def crew_detail(self, request, pk=None):
        """Get detailed information about a crew member including certificates and assignments"""
        crew = self.get_object()
        serializer = CrewDetailSerializer(crew)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_rank(self, request):
        """Get crew members filtered by rank"""
        rank = request.query_params.get('rank', None)
        if rank:
            crew = Crew.objects.filter(rank=rank)
            serializer = self.get_serializer(crew, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "Rank parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def by_certificate(self, request):
        """Get crew members who have a specific certificate type"""
        cert_type = request.query_params.get('certificate_type', None)
        if not cert_type:
            return Response(
                {"error": "certificate_type parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get crew members who have the specified certificate type
        crew_with_cert = Crew.objects.filter(
            certificates__certificate_type=cert_type
        ).distinct()
        
        serializer = self.get_serializer(crew_with_cert, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def with_expired_certificates(self, request):
        """Get crew members who have expired certificates"""
        today = timezone.now().date()
        
        crew_with_expired = Crew.objects.filter(
            certificates__expiry_date__lt=today
        ).distinct()
        
        serializer = self.get_serializer(crew_with_expired, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get crew members whose certificates are expiring soon"""
        days = int(request.query_params.get('days', 90))  # Default to 90 days
        today = timezone.now().date()
        expiry_cutoff = today + timedelta(days=days)
        
        crew_expiring_soon = Crew.objects.filter(
            certificates__expiry_date__gt=today,
            certificates__expiry_date__lte=expiry_cutoff
        ).distinct()
        
        serializer = self.get_serializer(crew_expiring_soon, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get crew members who are not currently assigned to a vessel"""
        assigned_crew_ids = CrewAssignment.objects.filter(
            is_current=True
        ).values_list('crew_id', flat=True)
        
        available_crew = Crew.objects.exclude(id__in=assigned_crew_ids)
        serializer = self.get_serializer(available_crew, many=True)
        return Response(serializer.data)


class CrewCertificateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Crew Certificates management.
    """
    queryset = CrewCertificate.objects.all()
    serializer_class = CrewCertificateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CertificateFilter
    search_fields = ['certificate_name', 'certificate_number', 'issuing_authority']
    ordering_fields = ['issue_date', 'expiry_date', 'created_at', 'updated_at']
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get all expired certificates"""
        today = timezone.now().date()
        expired = CrewCertificate.objects.filter(expiry_date__lt=today)
        serializer = self.get_serializer(expired, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get certificates expiring in the specified number of days"""
        days = int(request.query_params.get('days', 90))  # Default to 90 days
        today = timezone.now().date()
        expiry_cutoff = today + timedelta(days=days)
        
        expiring_soon = CrewCertificate.objects.filter(
            expiry_date__gt=today,
            expiry_date__lte=expiry_cutoff
        )
        
        serializer = self.get_serializer(expiring_soon, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_crew(self, request):
        """Get certificates for a specific crew member"""
        crew_id = request.query_params.get('crew_id', None)
        if not crew_id:
            return Response(
                {"error": "crew_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        certificates = CrewCertificate.objects.filter(crew_id=crew_id)
        serializer = self.get_serializer(certificates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def generate_notifications(self, request):
        """Generate notifications for certificates expiring soon"""
        days_thresholds = [30, 60, 90]  # Notify at 90, 60, and 30 days before expiry
        today = timezone.now().date()
        notifications_created = 0
        
        for days in days_thresholds:
            target_date = today + timedelta(days=days)
            # Find certificates expiring on the target date
            expiring_certs = CrewCertificate.objects.filter(
                expiry_date=target_date
            )
            
            for cert in expiring_certs:
                # Check if notification already exists for this certificate and threshold
                notification_exists = CertificateNotification.objects.filter(
                    certificate=cert,
                    days_before_expiry=days
                ).exists()
                
                if not notification_exists:
                    # Create notification
                    message = f"Certificate '{cert.certificate_name}' for {cert.crew.name} will expire in {days} days on {cert.expiry_date}."
                    CertificateNotification.objects.create(
                        certificate=cert,
                        days_before_expiry=days,
                        message=message,
                        sent_to=cert.crew.email
                    )
                    notifications_created += 1
        
        return Response({
            "message": f"Successfully generated {notifications_created} new notifications.",
            "notifications_created": notifications_created
        })


class CrewAssignmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Crew Assignments management.
    """
    queryset = CrewAssignment.objects.all()
    serializer_class = CrewAssignmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AssignmentFilter
    search_fields = ['crew__name', 'vessel__name', 'rank']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'updated_at']
    
    def perform_create(self, serializer):
        # When creating a new assignment, check for and close any current assignments
        crew = serializer.validated_data.get('crew')
        if crew:
            CrewAssignment.objects.filter(crew=crew, is_current=True).update(
                is_current=False,
                end_date=timezone.now().date()
            )
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get all current crew assignments"""
        current_assignments = CrewAssignment.objects.filter(is_current=True)
        serializer = self.get_serializer(current_assignments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_vessel(self, request):
        """Get crew assignments for a specific vessel"""
        vessel_id = request.query_params.get('vessel_id', None)
        if not vessel_id:
            return Response(
                {"error": "vessel_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        assignments = CrewAssignment.objects.filter(
            vessel_id=vessel_id,
            is_current=True
        )
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_crew(self, request):
        """Get assignments history for a specific crew member"""
        crew_id = request.query_params.get('crew_id', None)
        if not crew_id:
            return Response(
                {"error": "crew_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        assignments = CrewAssignment.objects.filter(crew_id=crew_id).order_by('-start_date')
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data)


class VesselViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Vessels management.
    """
    queryset = Vessel.objects.all()
    serializer_class = VesselSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'imo_number', 'vessel_type']
    ordering_fields = ['name', 'vessel_type']
    
    @action(detail=True, methods=['get'])
    def crew(self, request, pk=None):
        """Get current crew for a specific vessel"""
        vessel = self.get_object()
        assignments = CrewAssignment.objects.filter(vessel=vessel, is_current=True)
        serializer = CrewAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)


class CertificateNotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Certificate Notifications management.
    """
    queryset = CertificateNotification.objects.all()
    serializer_class = CertificateNotificationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'days_before_expiry']
    ordering_fields = ['notification_date', 'days_before_expiry']
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Mark a notification as acknowledged"""
        notification = self.get_object()
        notification.status = 'ACKNOWLEDGED'
        notification.acknowledged_by = request.user
        notification.acknowledged_at = timezone.now()
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark a notification as resolved"""
        notification = self.get_object()
        notification.status = 'RESOLVED'
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending notifications"""
        pending = CertificateNotification.objects.filter(status='PENDING')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)