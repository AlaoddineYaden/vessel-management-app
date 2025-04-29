from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Equipment, MaintenanceTask, MaintenanceHistory
from .serializers import (
    EquipmentSerializer, 
    MaintenanceTaskSerializer, 
    MaintenanceHistorySerializer,
    MaintenanceTaskListSerializer
)
from .utils import calculate_due_date, generate_notifications
from django.utils import timezone
from datetime import timedelta


class EquipmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing equipment
    """
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'manufacturer', 'location']
    search_fields = ['name', 'model', 'serial_number']
    ordering_fields = ['name', 'installation_date', 'status']
    
    @action(detail=True, methods=['get'])
    def maintenance_tasks(self, request, pk=None):
        """Get all maintenance tasks for specific equipment"""
        equipment = self.get_object()
        tasks = MaintenanceTask.objects.filter(equipment=equipment)
        serializer = MaintenanceTaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def maintenance_history(self, request, pk=None):
        """Get maintenance history for specific equipment"""
        equipment = self.get_object()
        history = MaintenanceHistory.objects.filter(equipment=equipment)
        serializer = MaintenanceHistorySerializer(history, many=True)
        return Response(serializer.data)


class MaintenanceTaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing maintenance tasks
    """
    queryset = MaintenanceTask.objects.all()
    serializer_class = MaintenanceTaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'equipment', 'responsible_role', 'interval_type']
    search_fields = ['task_name', 'description']
    ordering_fields = ['next_due_date', 'last_completed_date', 'status']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MaintenanceTaskListSerializer
        return MaintenanceTaskSerializer
    
    @action(detail=False, methods=['get'])
    def due_soon(self, request):
        """Get tasks due within the next 7 days"""
        due_date = timezone.now() + timedelta(days=7)
        tasks = MaintenanceTask.objects.filter(
            next_due_date__lte=due_date,
            status__in=['scheduled', 'overdue']
        )
        serializer = MaintenanceTaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue maintenance tasks"""
        now = timezone.now()
        tasks = MaintenanceTask.objects.filter(
            next_due_date__lt=now,
            status__in=['scheduled', 'in_progress']
        )
        serializer = MaintenanceTaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start_task(self, request, pk=None):
        """Mark a task as in progress"""
        task = self.get_object()
        task.status = 'in_progress'
        task.save()
        serializer = MaintenanceTaskSerializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete_task(self, request, pk=None):
        """Complete a maintenance task and create a history record"""
        task = self.get_object()
        
        # Get data for history entry
        remarks = request.data.get('remarks', '')
        running_hours = request.data.get('running_hours')
        parts_used = request.data.get('parts_used', '')
        duration = request.data.get('duration')
        
        # Create history record
        history_data = {
            'task': task,
            'equipment': task.equipment,
            'completed_by': request.user,
            'remarks': remarks,
            'running_hours': running_hours,
            'parts_used': parts_used,
            'duration': duration
        }
        
        history_serializer = MaintenanceHistorySerializer(data=history_data)
        if history_serializer.is_valid():
            history_serializer.save()
            
            # Update task status and dates
            task.status = 'completed'
            task.last_completed_date = timezone.now()
            task.next_due_date = task.calculate_next_due_date()
            task.save()
            
            # Create a new scheduled task for the next maintenance cycle
            task.status = 'scheduled'
            task.save()
            
            return Response({
                'task': MaintenanceTaskSerializer(task).data,
                'history': history_serializer.data
            })
        return Response(history_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def generate_notifications(self, request):
        """Generate notifications for upcoming and overdue tasks"""
        notifications = generate_notifications()
        return Response(notifications)
    
    @action(detail=True, methods=['post'])
    def cancel_task(self, request, pk=None):
        """Cancel a maintenance task"""
        task = self.get_object()
        task.status = 'cancelled'
        task.save()
        serializer = MaintenanceTaskSerializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get maintenance history for specific task"""
        task = self.get_object()
        history = MaintenanceHistory.objects.filter(task=task)
        serializer = MaintenanceHistorySerializer(history, many=True)
        return Response(serializer.data)


class MaintenanceHistoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for maintenance history
    """
    queryset = MaintenanceHistory.objects.all()
    serializer_class = MaintenanceHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['task', 'equipment', 'completed_by']
    search_fields = ['remarks', 'parts_used']
    ordering_fields = ['completed_date']
    
    def get_queryset(self):
        queryset = MaintenanceHistory.objects.all()
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(completed_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(completed_date__lte=end_date)
        
        return queryset