# audit_inspection/views.py

from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import (
    AuditType, Audit, AuditFinding, InspectionItem, 
    InspectionChecklist, Inspection, InspectionResult,
    AuditNotification, Vessel
)
from .serializers import (
    AuditTypeSerializer, AuditSerializer, AuditFindingSerializer,
    InspectionItemSerializer, InspectionChecklistSerializer,
    InspectionSerializer, InspectionResultSerializer,
    AuditNotificationSerializer, VesselSerializer
)
from .permissions import IsAuditorOrReadOnly, IsInspectorOrReadOnly


class VesselViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing vessels"""
    queryset = Vessel.objects.all()
    serializer_class = VesselSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'imo_number']


class AuditTypeViewSet(viewsets.ModelViewSet):
    """API endpoint for audit types"""
    queryset = AuditType.objects.all()
    serializer_class = AuditTypeSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissionsOrAnonReadOnly]


class AuditViewSet(viewsets.ModelViewSet):
    """API endpoint for audits"""
    queryset = Audit.objects.all().select_related('audit_type', 'auditor', 'vessel', 'created_by')
    serializer_class = AuditSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuditorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['audit_type', 'status', 'vessel', 'auditor']
    search_fields = ['comments', 'vessel__name', 'audit_type__name']
    ordering_fields = ['planned_date', 'actual_date', 'created_at', 'updated_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        
        if from_date:
            queryset = queryset.filter(planned_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(planned_date__lte=to_date)
        
        # Filter for upcoming audits
        upcoming = self.request.query_params.get('upcoming')
        if upcoming:
            days = int(upcoming)
            today = timezone.now().date()
            queryset = queryset.filter(
                planned_date__gte=today,
                planned_date__lte=today + timezone.timedelta(days=days),
                status='PLANNED'
            )
        
        # Filter for overdue audits
        overdue = self.request.query_params.get('overdue')
        if overdue and overdue.lower() == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(
                Q(planned_date__lt=today) & Q(status='PLANNED') |
                Q(status='OVERDUE')
            )
        
        return queryset
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_report(self, request, pk=None):
        """Upload audit report"""
        audit = self.get_object()
        
        if 'report_file' not in request.FILES:
            return Response(
                {'error': 'No report file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        audit.report_file = request.FILES['report_file']
        audit.save()
        
        serializer = self.get_serializer(audit)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update audit status"""
        audit = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'No status provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_transitions = {
            'PLANNED': ['IN_PROGRESS', 'CANCELLED', 'OVERDUE'],
            'IN_PROGRESS': ['COMPLETED', 'CANCELLED'],
            'COMPLETED': [],
            'CANCELLED': [],
            'OVERDUE': ['IN_PROGRESS', 'CANCELLED'],
        }
        
        if new_status not in valid_transitions[audit.status]:
            return Response(
                {'error': f'Invalid status transition from {audit.status} to {new_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If completing the audit, require actual_date
        if new_status == 'COMPLETED' and not audit.actual_date:
            if 'actual_date' in request.data:
                audit.actual_date = request.data['actual_date']
            else:
                return Response(
                    {'error': 'Actual date is required when completing an audit'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        audit.status = new_status
        audit.save()
        
        serializer = self.get_serializer(audit)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def due_notifications(self, request):
        """Get audit due notifications"""
        # Generate the notifications first
        from django.core.management import call_command
        call_command('generate_notifications')
        
        # Then return all active notifications
        notifications = AuditNotification.objects.filter(
            is_sent=False
        ).select_related('audit', 'finding')
        
        serializer = AuditNotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class AuditFindingViewSet(viewsets.ModelViewSet):
    """API endpoint for audit findings"""
    queryset = AuditFinding.objects.all().select_related('audit', 'assigned_to')
    serializer_class = AuditFindingSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuditorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['audit', 'severity', 'status', 'assigned_to']
    search_fields = ['description', 'corrective_action']
    ordering_fields = ['due_date', 'closed_date', 'created_at', 'updated_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtering by audit ID from the URL
        audit_id = self.request.query_params.get('audit_id')
        if audit_id:
            queryset = queryset.filter(audit_id=audit_id)
        
        # Filter by overdue findings
        overdue = self.request.query_params.get('overdue')
        if overdue and overdue.lower() == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(
                due_date__lt=today,
                status__in=['OPEN', 'IN_PROGRESS']
            )
        
        # Filter by assigned to the current user
        assigned_to_me = self.request.query_params.get('assigned_to_me')
        if assigned_to_me and assigned_to_me.lower() == 'true':
            queryset = queryset.filter(assigned_to=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_attachment(self, request, pk=None):
        """Upload finding attachment"""
        finding = self.get_object()
        
        if 'attachments' not in request.FILES:
            return Response(
                {'error': 'No attachment file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        finding.attachments = request.FILES['attachments']
        finding.save()
        
        serializer = self.get_serializer(finding)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update finding status"""
        finding = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'No status provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_transitions = {
            'OPEN': ['IN_PROGRESS', 'CLOSED'],
            'IN_PROGRESS': ['CLOSED'],
            'CLOSED': ['VERIFIED'],
            'VERIFIED': [],
        }
        
        if new_status not in valid_transitions[finding.status]:
            return Response(
                {'error': f'Invalid status transition from {finding.status} to {new_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If closing the finding, record the closed date
        if new_status == 'CLOSED' and not finding.closed_date:
            finding.closed_date = timezone.now().date()
        
        finding.status = new_status
        finding.save()
        
        serializer = self.get_serializer(finding)
        return Response(serializer.data)


class InspectionItemViewSet(viewsets.ModelViewSet):
    """API endpoint for inspection items"""
    queryset = InspectionItem.objects.all()
    serializer_class = InspectionItemSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissionsOrAnonReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_mandatory']
    search_fields = ['name', 'description', 'regulation_reference']


class InspectionChecklistViewSet(viewsets.ModelViewSet):
    """API endpoint for inspection checklists"""
    queryset = InspectionChecklist.objects.all().prefetch_related('items')
    serializer_class = InspectionChecklistSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissionsOrAnonReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    @action(detail=True, methods=['post'])
    def add_items(self, request, pk=None):
        """Add items to a checklist"""
        checklist = self.get_object()
        item_ids = request.data.get('item_ids', [])
        
        if not item_ids:
            return Response(
                {'error': 'No item IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        items = InspectionItem.objects.filter(id__in=item_ids)
        checklist.items.add(*items)
        
        serializer = self.get_serializer(checklist)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def remove_items(self, request, pk=None):
        """Remove items from a checklist"""
        checklist = self.get_object()
        item_ids = request.data.get('item_ids', [])
        
        if not item_ids:
            return Response(
                {'error': 'No item IDs provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        items = InspectionItem.objects.filter(id__in=item_ids)
        checklist.items.remove(*items)
        
        serializer = self.get_serializer(checklist)
        return Response(serializer.data)


class InspectionViewSet(viewsets.ModelViewSet):
    """API endpoint for inspections"""
    queryset = Inspection.objects.all().select_related('checklist', 'vessel', 'inspector', 'created_by')
    serializer_class = InspectionSerializer
    permission_classes = [permissions.IsAuthenticated, IsInspectorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['checklist', 'status', 'vessel', 'inspector']
    search_fields = ['comments', 'vessel__name', 'checklist__name']
    ordering_fields = ['planned_date', 'actual_date', 'created_at', 'updated_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        
        if from_date:
            queryset = queryset.filter(planned_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(planned_date__lte=to_date)
        
        # Filter for upcoming inspections
        upcoming = self.request.query_params.get('upcoming')
        if upcoming:
            days = int(upcoming)
            today = timezone.now().date()
            queryset = queryset.filter(
                planned_date__gte=today,
                planned_date__lte=today + timezone.timedelta(days=days),
                status='PLANNED'
            )
        
        # Filter for overdue inspections
        overdue = self.request.query_params.get('overdue')
        if overdue and overdue.lower() == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(
                Q(planned_date__lt=today) & Q(status='PLANNED') |
                Q(status='OVERDUE')
            )
        
        return queryset
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_report(self, request, pk=None):
        """Upload inspection report"""
        inspection = self.get_object()
        
        if 'report_file' not in request.FILES:
            return Response(
                {'error': 'No report file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        inspection.report_file = request.FILES['report_file']
        inspection.save()
        
        serializer = self.get_serializer(inspection)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update inspection status"""
        inspection = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'No status provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_transitions = {
            'PLANNED': ['IN_PROGRESS', 'CANCELLED', 'OVERDUE'],
            'IN_PROGRESS': ['COMPLETED', 'CANCELLED'],
            'COMPLETED': [],
            'CANCELLED': [],
            'OVERDUE': ['IN_PROGRESS', 'CANCELLED'],
        }
        
        if new_status not in valid_transitions[inspection.status]:
            return Response(
                {'error': f'Invalid status transition from {inspection.status} to {new_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If completing the inspection, require actual_date
        if new_status == 'COMPLETED' and not inspection.actual_date:
            if 'actual_date' in request.data:
                inspection.actual_date = request.data['actual_date']
            else:
                return Response(
                    {'error': 'Actual date is required when completing an inspection'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        inspection.status = new_status
        inspection.save()
        
        serializer = self.get_serializer(inspection)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def generate_results(self, request, pk=None):
        """Generate initial results for all checklist items"""
        inspection = self.get_object()
        
        if inspection.results.exists():
            return Response(
                {'error': 'This inspection already has results'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create result entries for all items in the checklist
        results = []
        for item in inspection.checklist.items.all():
            result = InspectionResult(
                inspection=inspection,
                item=item,
                result='NOT_CHECKED'
            )
            results.append(result)
        
        InspectionResult.objects.bulk_create(results)
        
        inspection.refresh_from_db()
        serializer = self.get_serializer(inspection)
        return Response(serializer.data)


class InspectionResultViewSet(viewsets.ModelViewSet):
    """API endpoint for inspection results"""
    queryset = InspectionResult.objects.all().select_related('inspection', 'item')
    serializer_class = InspectionResultSerializer
    permission_classes = [permissions.IsAuthenticated, IsInspectorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['inspection', 'result']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by inspection ID
        inspection_id = self.request.query_params.get('inspection_id')
        if inspection_id:
            queryset = queryset.filter(inspection_id=inspection_id)
        
        # Filter by item category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(item__category=category)
        
        return queryset
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_evidence(self, request, pk=None):
        """Upload evidence file for inspection result"""
        result = self.get_object()
        
        if 'evidence_file' not in request.FILES:
            return Response(
                {'error': 'No evidence file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        result.evidence_file = request.FILES['evidence_file']
        result.save()
        
        serializer = self.get_serializer(result)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'])
    def bulk_update(self, request):
        """Update multiple inspection results at once"""
        results_data = request.data.get('results', [])
        
        if not results_data:
            return Response(
                {'error': 'No results provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_results = []
        for result_data in results_data:
            if 'id' not in result_data:
                continue
                
            result = get_object_or_404(InspectionResult, id=result_data['id'])
            
            # Check permissions
            if not IsInspectorOrReadOnly().has_object_permission(request, self, result):
                return Response(
                    {'error': f'Permission denied for result {result.id}'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Update fields
            if 'result' in result_data:
                result.result = result_data['result']
            if 'comments' in result_data:
                result.comments = result_data['comments']
                
            result.save()
            updated_results.append(result)
        
        serializer = self.get_serializer(updated_results, many=True)
        return Response(serializer.data)


class AuditNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for audit notifications"""
    queryset = AuditNotification.objects.all().select_related('audit', 'finding')
    serializer_class = AuditNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['notification_type', 'is_sent']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Only show notifications for this user
        queryset = queryset.filter(recipients=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def mark_as_sent(self, request, pk=None):
        """Mark notification as sent"""
        notification = self.get_object()
        notification.is_sent = True
        notification.sent_date = timezone.now()
        notification.save()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
