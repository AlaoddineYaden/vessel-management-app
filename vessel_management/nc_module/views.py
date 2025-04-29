from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q

from .models import NonConformity, CorrectiveAction, EvidenceFile, PreventiveAction
from .serializers import (
    NonConformitySerializer, CorrectiveActionSerializer,
    EvidenceFileSerializer, PreventiveActionSerializer
)
from .filters import (
    NonConformityFilter, CorrectiveActionFilter,
    PreventiveActionFilter
)
from .services import (
    get_overdue_actions, get_vessel_nonconformities,
    get_user_assignments, close_nonconformity,
    verify_corrective_action
)
from .notifications import (
    send_nonconformity_notification,
    send_action_assignment_notification,
    send_action_due_reminder
)


class NonConformityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing non-conformities.
    """
    queryset = NonConformity.objects.all()
    serializer_class = NonConformitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = NonConformityFilter
    search_fields = ['description', 'root_cause', 'source_id']
    ordering_fields = ['id', 'detection_date', 'severity', 'status', 'created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        # Send notification
        send_nonconformity_notification(serializer.instance.id)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """
        Close a non-conformity and update related actions.
        """
        success = close_nonconformity(pk, request.user)
        if success:
            return Response({'status': 'non-conformity closed'})
        return Response(
            {'error': 'non-conformity not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'])
    def vessel(self, request):
        """
        Get non-conformities for a specific vessel.
        """
        vessel_id = request.query_params.get('vessel_id')
        status_filter = request.query_params.get('status')
        
        if not vessel_id:
            return Response(
                {'error': 'vessel_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        nonconformities = get_vessel_nonconformities(vessel_id, status_filter)
        serializer = self.get_serializer(nonconformities, many=True)
        return Response(serializer.data)


class CorrectiveActionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing corrective actions.
    """
    queryset = CorrectiveAction.objects.all()
    serializer_class = CorrectiveActionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CorrectiveActionFilter
    search_fields = ['description', 'verification_comments']
    ordering_fields = ['id', 'due_date', 'completed_date', 'verification_status', 'created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save()
        # Send notification
        send_action_assignment_notification(serializer.instance.id, 'corrective')
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Verify or reject a corrective action.
        """
        verified = request.data.get('verified', True)
        comments = request.data.get('comments')
        
        success = verify_corrective_action(pk, request.user, verified, comments)
        if success:
            return Response({'status': 'corrective action verified'})
        return Response(
            {'error': 'corrective action not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get all overdue corrective actions.
        """
        overdue_actions = get_overdue_actions()['corrective_actions']
        serializer = self.get_serializer(overdue_actions, many=True)
        return Response(serializer.data)


class EvidenceFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing evidence files.
    """
    queryset = EvidenceFile.objects.all()
    serializer_class = EvidenceFileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['file']
    ordering_fields = ['id', 'uploaded_at']
    ordering = ['-uploaded_at']
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class PreventiveActionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing preventive actions.
    """
    queryset = PreventiveAction.objects.all()
    serializer_class = PreventiveActionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PreventiveActionFilter
    search_fields = ['description']
    ordering_fields = ['id', 'due_date', 'completed_date', 'status', 'created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save()
        # Send notification
        send_action_assignment_notification(serializer.instance.id, 'preventive')
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get all overdue preventive actions.
        """
        overdue_actions = get_overdue_actions()['preventive_actions']
        serializer = self.get_serializer(overdue_actions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_assignments(self, request):
        """
        Get all actions assigned to the current user.
        """
        include_completed = request.query_params.get('include_completed', 'false').lower() == 'true'
        assignments = get_user_assignments(request.user.id, include_completed)
        
        corrective_serializer = CorrectiveActionSerializer(assignments['corrective_actions'], many=True)
        preventive_serializer = self.get_serializer(assignments['preventive_actions'], many=True)
        
        return Response({
            'corrective_actions': corrective_serializer.data,
            'preventive_actions': preventive_serializer.data
        })
