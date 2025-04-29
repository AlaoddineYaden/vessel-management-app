from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
import csv
import io
import json
from datetime import datetime

from .models import ISMRequirement, ComplianceItem, ComplianceEvidence, ComplianceReview
from .serializers import (
    ISMRequirementSerializer,
    ComplianceItemSerializer,
    ComplianceItemDetailSerializer,
    ComplianceItemListSerializer,
    ComplianceEvidenceSerializer,
    ComplianceReviewSerializer,
    ComplianceReportSerializer
)
from .filters import ISMRequirementFilter, ComplianceItemFilter, ComplianceReviewFilter
from .services import ComplianceService


class ISMRequirementViewSet(viewsets.ModelViewSet):
    """API endpoint for ISM requirements"""
    queryset = ISMRequirement.objects.all()
    serializer_class = ISMRequirementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ISMRequirementFilter
    search_fields = ['requirement_code', 'requirement_text', 'guidance_notes']
    ordering_fields = ['ism_section', 'requirement_code', 'created_at', 'updated_at']
    
    @action(detail=False, methods=['get'])
    def sections(self, request):
        """Get all ISM sections with counts of requirements"""
        sections = {}
        for choice in ISMRequirement.ISM_SECTION_CHOICES:
            code, name = choice
            count = ISMRequirement.objects.filter(ism_section=code).count()
            sections[code] = {
                'name': name,
                'count': count
            }
        return Response(sections)


class ComplianceItemViewSet(viewsets.ModelViewSet):
    """API endpoint for compliance items"""
    queryset = ComplianceItem.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ComplianceItemFilter
    ordering_fields = ['assessment_date', 'next_review_date', 'compliance_status', 'risk_level']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ComplianceItemListSerializer 
        elif self.action in ['retrieve', 'update', 'partial_update', 'create']:
            return ComplianceItemDetailSerializer
        return ComplianceItemSerializer
    
    def perform_create(self, serializer):
        """Set assessor and calculate risk level and next review date"""
        instance = serializer.save(assessor=self.request.user)
        
        # Calculate risk level
        risk_level = ComplianceService.calculate_risk_level(instance)
        next_review_date = ComplianceService.schedule_next_review(instance)
        
        # Update the instance with calculated values
        ComplianceItem.objects.filter(pk=instance.pk).update(
            risk_level=risk_level,
            next_review_date=next_review_date
        )
    
    def perform_update(self, serializer):
        """Update risk level and review date on status change"""
        instance = serializer.save()
        
        # Calculate risk level and next review date if status has changed
        if 'compliance_status' in serializer.validated_data:
            risk_level = ComplianceService.calculate_risk_level(instance)
            next_review_date = ComplianceService.schedule_next_review(instance)
            
            # Update the instance with calculated values
            ComplianceItem.objects.filter(pk=instance.pk).update(
                risk_level=risk_level,
                next_review_date=next_review_date
            )
    
    @action(detail=False, methods=['get'])
    def vessel_compliance(self, request):
        """Get compliance status for a vessel"""
        vessel_id = request.query_params.get('vessel_id')
        if not vessel_id:
            return Response(
                {"error": "vessel_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        metrics = ComplianceService.calculate_compliance_metrics(vessel_id)
        return Response(metrics)
    
    @action(detail=False, methods=['get'])
    def gap_analysis(self, request):
        """Generate gap analysis for a vessel"""
        vessel_id = request.query_params.get('vessel_id')
        if not vessel_id:
            return Response(
                {"error": "vessel_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        gap_analysis = ComplianceService.generate_gap_analysis(vessel_id)
        return Response(gap_analysis)
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get summary metrics for dashboard"""
        vessel_id = request.query_params.get('vessel_id')
        if not vessel_id:
            return Response(
                {"error": "vessel_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        metrics = ComplianceService.calculate_compliance_metrics(vessel_id)
        
        # Add high-priority items that need attention
        high_risk_items = ComplianceItem.objects.filter(
            vessel_id=vessel_id,
            risk_level='high'
        ).select_related('ism_requirement')[:5]
        
        upcoming_reviews = ComplianceReview.objects.filter(
            compliance_item__vessel_id=vessel_id,
            status='scheduled',
            scheduled_date__gte=timezone.now()
        ).order_by('scheduled_date')[:5]
        
        # Serialize the items for the response
        serialized_risk_items = ComplianceItemListSerializer(high_risk_items, many=True).data
        serialized_reviews = ComplianceReviewSerializer(upcoming_reviews, many=True).data
        
        summary = {
            **metrics,
            'high_risk_items_details': serialized_risk_items,
            'upcoming_reviews': serialized_reviews
        }
        
        return Response(summary)


class ComplianceEvidenceViewSet(viewsets.ModelViewSet):
    """API endpoint for compliance evidence"""
    queryset = ComplianceEvidence.objects.all()
    serializer_class = ComplianceEvidenceSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """Filter evidence by compliance item if specified"""
        queryset = ComplianceEvidence.objects.all()
        compliance_item_id = self.request.query_params.get('compliance_item')
        if compliance_item_id:
            queryset = queryset.filter(compliance_item__id=compliance_item_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class ComplianceReviewViewSet(viewsets.ModelViewSet):
    """API endpoint for compliance reviews"""
    queryset = ComplianceReview.objects.all()
    serializer_class = ComplianceReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ComplianceReviewFilter
    ordering_fields = ['scheduled_date', 'actual_review_date', 'status']
    
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete_review(self, request, pk=None):
        """Mark a review as completed and update the compliance item"""
        review = self.get_object()
        
        if review.status == 'completed':
            return Response(
                {"error": "Review is already completed"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Update review status
        serializer = self.get_serializer(review, data={
            'status': 'completed',
            'actual_review_date': timezone.now(),
            'findings': request.data.get('findings', ''),
            'recommendations': request.data.get('recommendations', '')
        }, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            # Update compliance item if status is provided
            compliance_status = request.data.get('compliance_status')
            if compliance_status:
                compliance_item = review.compliance_item
                compliance_item.compliance_status = compliance_status
                compliance_item.assessment_date = timezone.now()
                
                # Recalculate risk level and next review
                compliance_item.risk_level = ComplianceService.calculate_risk_level(compliance_item)
                compliance_item.next_review_date = ComplianceService.schedule_next_review(compliance_item)
                compliance_item.save()
                
                # Schedule next review if applicable
                if compliance_status in ['non_compliant', 'partially_compliant']:
                    ComplianceReview.objects.create(
                        compliance_item=compliance_item,
                        scheduled_date=compliance_item.next_review_date,
                        status='scheduled'
                    )
            
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComplianceReportViewSet(viewsets.ViewSet):
    """API endpoint for generating compliance reports"""
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        """Generate a compliance report"""
        serializer = ComplianceReportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        vessel_id = data['vessel_id']
        report_format = data['format']
        include_evidence = data['include_evidence']
        include_reviews = data['include_reviews']
        
        # Filter items by vessel and date range if provided
        queryset = ComplianceItem.objects.filter(vessel_id=vessel_id)
        
        if 'start_date' in data:
            queryset = queryset.filter(assessment_date__gte=data['start_date'])
        
        if 'end_date' in data:
            queryset = queryset.filter(assessment_date__lte=data['end_date'])
            
        # Get compliance metrics
        metrics = ComplianceService.calculate_compliance_metrics(vessel_id)
        gap_analysis = ComplianceService.generate_gap_analysis(vessel_id)
        
        # Create the report based on requested format
        if report_format == 'json':
            # Create JSON report
            items_data = []
            for item in queryset.select_related('ism_requirement'):
                item_data = {
                    'id': str(item.id),
                    'requirement_code': item.ism_requirement.requirement_code,
                    'requirement_text': item.ism_requirement.requirement_text,
                    'ism_section': item.ism_requirement.ism_section,
                    'compliance_status': item.compliance_status,
                    'risk_level': item.risk_level,
                    'assessment_date': item.assessment_date.isoformat(),
                    'next_review_date': item.next_review_date.isoformat() if item.next_review_date else None,
                    'comments': item.comments,
                }
                
                # Include evidence if requested
                if include_evidence:
                    evidence_data = []
                    for evidence in item.evidence.all():
                        evidence_data.append({
                            'id': str(evidence.id),
                            'title': evidence.title,
                            'description': evidence.description,
                            'evidence_type': evidence.evidence_type,
                            'file': evidence.file.url if evidence.file else None,
                            'reference_url': evidence.reference_url,
                            'upload_date': evidence.upload_date.isoformat(),
                        })
                    item_data['evidence'] = evidence_data
                
                # Include reviews if requested
                if include_reviews:
                    review_data = []
                    for review in item.reviews.all():
                        review_data.append({
                            'id': str(review.id),
                            'scheduled_date': review.scheduled_date.isoformat(),
                            'actual_review_date': review.actual_review_date.isoformat() if review.actual_review_date else None,
                            'status': review.status,
                            'findings': review.findings,
                            'recommendations': review.recommendations,
                        })
                    item_data['reviews'] = review_data
                
                items_data.append(item_data)
            
            # Complete report data
            report_data = {
                'vessel_id': str(vessel_id),
                'report_date': timezone.now().isoformat(),
                'metrics': metrics,
                'gap_analysis': gap_analysis,
                'items': items_data,
            }
            
            return Response(report_data)
            
        elif report_format == 'csv':
            # Create CSV report
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header row
            header = ['ISM Section', 'Requirement Code', 'Requirement Text', 'Status', 
                     'Risk Level', 'Assessment Date', 'Next Review Date', 'Comments']
            
            if include_evidence:
                header.extend(['Evidence'])
            
            if include_reviews:
                header.extend(['Latest Review Status', 'Latest Review Date', 'Findings'])
                
            writer.writerow(header)
            
            # Write data rows
            for item in queryset.select_related('ism_requirement'):
                row = [
                    item.ism_requirement.ism_section,
                    item.ism_requirement.requirement_code,
                    item.ism_requirement.requirement_text,
                    item.compliance_status,
                    item.risk_level,
                    item.assessment_date.strftime('%Y-%m-%d'),
                    item.next_review_date.strftime('%Y-%m-%d') if item.next_review_date else '',
                    item.comments
                ]
                
                if include_evidence:
                    evidence_list = ', '.join([e.title for e in item.evidence.all()])
                    row.append(evidence_list)
                
                if include_reviews:
                    latest_review = item.reviews.order_by('-actual_review_date').first()
                    if latest_review:
                        row.extend([
                            latest_review.status,
                            latest_review.actual_review_date.strftime('%Y-%m-%d') if latest_review.actual_review_date else '',
                            latest_review.findings
                        ])
                    else:
                        row.extend(['', '', ''])
                
                writer.writerow(row)
            
            # Create response
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="ism_compliance_report_{datetime.now().strftime("%Y%m%d")}.csv"'
            return response
            
        elif report_format == 'pdf':
            # For PDF generation, we would typically use a library like ReportLab or WeasyPrint
            # This implementation is left as a placeholder - in a real implementation, you would
            # generate a PDF using one of these libraries
            return Response(
                {"error": "PDF format not implemented in this example module"},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
        
        return Response(
            {"error": "Invalid report format"},
            status=status.HTTP_400_BAD_REQUEST
        )