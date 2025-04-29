from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .models import Report, SavedReport, ReportSchedule, DashboardMetric
from .serializers import (
    ReportSerializer,
    SavedReportSerializer,
    ReportScheduleSerializer,
    DashboardMetricSerializer
)
from .tasks import generate_report
from .services.exporters import ExporterFactory


class ReportViewSet(viewsets.ModelViewSet):
    """API endpoints for managing report definitions"""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'report_type']
    ordering_fields = ['name', 'report_type', 'created_date']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate a report with the given parameters"""
        report = self.get_object()
        parameters = request.data.get('parameters', {})
        
        # Generate the report
        report_data = generate_report(report.id, parameters)
        
        # Create a saved report
        saved_report = SavedReport.objects.create(
            report=report,
            parameters_used=parameters,
            result_data=report_data,
            file_format='json',
            generated_by=request.user
        )
        
        return Response({
            'report_id': saved_report.id,
            'generated_at': saved_report.generated_date.isoformat()
        })
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export a report in the specified format"""
        report = self.get_object()
        format_type = request.query_params.get('format', 'json')
        parameters = request.query_params.get('parameters', {})
        
        # Generate the report
        report_data = generate_report(report.id, parameters)
        
        # Export the report
        exporter = ExporterFactory.create_exporter(report_data, format_type)
        exported_data = exporter.export()
        
        # Create response
        response = HttpResponse(exported_data)
        response['Content-Type'] = f'application/{format_type}'
        response['Content-Disposition'] = f'attachment; filename="{report.name}.{format_type}"'
        
        return response


class SavedReportViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoints for accessing saved reports"""
    queryset = SavedReport.objects.all().order_by('-generated_date')
    serializer_class = SavedReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['report__name', 'report__report_type']
    ordering_fields = ['generated_date', 'report__name']
    
    def get_queryset(self):
        """Filter queryset to only show reports created by the user"""
        return super().get_queryset().filter(generated_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download a saved report"""
        saved_report = self.get_object()
        
        # Export the report
        exporter = ExporterFactory.create_exporter(
            saved_report.result_data,
            saved_report.file_format
        )
        exported_data = exporter.export()
        
        # Create response
        response = HttpResponse(exported_data)
        response['Content-Type'] = f'application/{saved_report.file_format}'
        response['Content-Disposition'] = (
            f'attachment; filename="{saved_report.report.name}.{saved_report.file_format}"'
        )
        
        return response


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """API endpoints for managing report schedules"""
    queryset = ReportSchedule.objects.all().order_by('-created_date')
    serializer_class = ReportScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'report__name', 'frequency']
    ordering_fields = ['name', 'frequency', 'created_date', 'last_run']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle the active status of a schedule"""
        schedule = self.get_object()
        schedule.is_active = not schedule.is_active
        schedule.save()
        return Response({'is_active': schedule.is_active})
    
    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        """Execute a scheduled report immediately"""
        schedule = self.get_object()
        
        # Generate the report
        report_data = generate_report(schedule.report.id, schedule.parameters)
        
        # Create a saved report
        saved_report = SavedReport.objects.create(
            report=schedule.report,
            parameters_used=schedule.parameters,
            result_data=report_data,
            file_format=schedule.output_format,
            generated_by=request.user
        )
        
        # Export the report
        exporter = ExporterFactory.create_exporter(
            report_data,
            schedule.output_format
        )
        exported_data = exporter.export()
        
        # Save the exported file
        saved_report.file_location = f"reports/{saved_report.id}.{schedule.output_format}"
        saved_report.save()
        
        return Response({
            'report_id': saved_report.id,
            'generated_at': saved_report.generated_date.isoformat()
        })


class DashboardMetricViewSet(viewsets.ModelViewSet):
    """API endpoints for managing dashboard metrics"""
    queryset = DashboardMetric.objects.all().order_by('display_order')
    serializer_class = DashboardMetricSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'metric_type']
    ordering_fields = ['name', 'display_order', 'created_date']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """Refresh a specific metric"""
        metric = self.get_object()
        
        # Calculate the metric value based on its type
        if metric.metric_type == 'compliance':
            calculator = ComplianceMetrics()
        elif metric.metric_type == 'maintenance':
            calculator = MaintenanceMetrics()
        elif metric.metric_type == 'certification':
            calculator = CertificationMetrics()
        else:
            return Response({'error': 'Invalid metric type'}, status=400)
        
        # Calculate and update the metric
        result = calculator.calculate_metric(metric)
        metric.last_value = result
        metric.last_calculated = timezone.now()
        metric.save()
        
        return Response({
            'value': result,
            'calculated_at': metric.last_calculated.isoformat()
        })
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get all active metrics for the dashboard"""
        metrics = self.get_queryset().filter(is_active=True)
        
        # Calculate values for each metric
        results = []
        for metric in metrics:
            if metric.metric_type == 'compliance':
                calculator = ComplianceMetrics()
            elif metric.metric_type == 'maintenance':
                calculator = MaintenanceMetrics()
            elif metric.metric_type == 'certification':
                calculator = CertificationMetrics()
            else:
                continue
            
            result = calculator.calculate_metric(metric)
            results.append({
                'id': metric.id,
                'name': metric.name,
                'description': metric.description,
                'metric_type': metric.metric_type,
                'value': result,
                'display_order': metric.display_order
            })
        
        return Response(results) 