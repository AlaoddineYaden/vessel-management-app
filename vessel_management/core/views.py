# 10. core/views.py
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vessel, SystemLog, File
from .serializers import VesselSerializer, SystemLogSerializer, FileSerializer
from utils.permissions import IsAdmin, IsFleetManager, IsCrew

class VesselViewSet(viewsets.ModelViewSet):
    queryset = Vessel.objects.all()
    serializer_class = VesselSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vessel_type', 'flag', 'is_active']
    search_fields = ['name', 'imo_number', 'mmsi_number', 'call_sign']
    ordering_fields = ['name', 'build_year', 'gross_tonnage', 'created_at']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, (IsAdmin | IsFleetManager)]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

class SystemLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'source']
    search_fields = ['message', 'source']
    ordering_fields = ['created_at', 'level']

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['file_type', 'content_type_name']
    search_fields = ['file_name', 'description']
    ordering_fields = ['created_at', 'file_name', 'file_size']
    
    def get_permissions(self):
        if self.action in ['destroy']:
            permission_classes = [IsAuthenticated, IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        file_obj = self.request.FILES.get('file')
        
        if not file_obj:
            raise serializers.ValidationError({"file": "No file was submitted."})
        
        # Extract file information
        file_size = file_obj.size
        file_name = file_obj.name
        content_type = file_obj.content_type
        file_extension = file_name.split('.')[-1] if '.' in file_name else ''
        
        serializer.save(
            created_by=self.request.user,
            file_name=file_name,
            file_size=file_size,
            file_type=file_extension,
            content_type=content_type
        )
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
