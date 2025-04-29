from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q

from .models import (
    ProcedureCategory, Procedure, ProcedureVersion,
    ProcedureReview, ProcedureAcknowledgment
)
from .serializers import (
    ProcedureCategorySerializer, ProcedureSerializer, ProcedureDetailSerializer,
    ProcedureReviewSerializer, ProcedureVersionSerializer, ProcedureAcknowledgmentSerializer
)
from .utils import generate_next_version


class ProcedureCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProcedureCategory.objects.all()
    serializer_class = ProcedureCategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'code']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['order', 'code', 'name']


class ProcedureViewSet(viewsets.ModelViewSet):
    queryset = Procedure.objects.filter(is_active=True)
    serializer_class = ProcedureSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'category', 'review_status', 'is_active']
    search_fields = ['title', 'content', 'tags']
    ordering_fields = ['title', 'created_date', 'last_reviewed_date', 'next_review_date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProcedureDetailSerializer
        return ProcedureSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """Create a new version of a procedure"""
        procedure = self.get_object()
        next_version = generate_next_version(procedure.version)
        
        if 'version' in request.data:
            next_version = request.data['version']
        
        new_procedure = procedure.create_new_version(next_version, request.user)
        
        # If change notes are provided, save them to the version history
        if 'change_notes' in request.data:
            version = ProcedureVersion.objects.filter(procedure=new_procedure).first()
            if version:
                version.change_notes = request.data['change_notes']
                version.save()
        
        serializer = ProcedureDetailSerializer(new_procedure)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Add a review for a procedure"""
        procedure = self.get_object()
        
        serializer = ProcedureReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                procedure=procedure,
                reviewed_by=request.user
            )
            
            # Update the procedure's review status
            procedure.last_reviewed_date = timezone.now()
            procedure.next_review_date = procedure.last_reviewed_date + \
                                       timezone.timedelta(days=30 * procedure.review_interval_months)
            
            if review.approved:
                procedure.review_status = 'CURRENT'
            elif review.changes_required:
                procedure.review_status = 'IN_REVIEW'
            
            procedure.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge a procedure"""
        procedure = self.get_object()
        
        # Check if user already acknowledged this version
        existing = ProcedureAcknowledgment.objects.filter(
            procedure=procedure,
            user=request.user,
            acknowledged_version=procedure.version
        ).first()
        
        if existing:
            serializer = ProcedureAcknowledgmentSerializer(existing)
            return Response(serializer.data)
        
        acknowledgment = ProcedureAcknowledgment.objects.create(
            procedure=procedure,
            user=request.user,
            acknowledged_version=procedure.version,
            comments=request.data.get('comments', '')
        )
        
        serializer = ProcedureAcknowledgmentSerializer(acknowledgment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search endpoint for procedures"""
        query = request.query_params.get('q', '')
        category_id = request.query_params.get('category', None)
        document_type = request.query_params.get('document_type', None)
        review_status = request.query_params.get('review_status', None)
        tag = request.query_params.get('tag', None)
        
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) |
                Q(tags__icontains=query)
            )
        
        if category_id:
            categories = ProcedureCategory.objects.filter(
                Q(id=category_id) | Q(parent_id=category_id)
            )
            queryset = queryset.filter(category__in=categories)
        
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        
        if review_status:
            queryset = queryset.filter(review_status=review_status)
        
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def review_due(self, request):
        """Get procedures due for review"""
        days = int(request.query_params.get('days', 30))
        due_date = timezone.now() + timezone.timedelta(days=days)
        
        queryset = self.get_queryset().filter(
            Q(next_review_date__lte=due_date) |
            Q(review_status__in=['DUE_SOON', 'OVERDUE'])
        ).order_by('next_review_date')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProcedureReviewViewSet(viewsets.ModelViewSet):
    queryset = ProcedureReview.objects.all()
    serializer_class = ProcedureReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['procedure', 'reviewed_by', 'approved']
    ordering_fields = ['review_date']
    
    def perform_create(self, serializer):
        serializer.save(reviewed_by=self.request.user)


class ProcedureAcknowledgmentViewSet(viewsets.ModelViewSet):
    queryset = ProcedureAcknowledgment.objects.all()
    serializer_class = ProcedureAcknowledgmentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['procedure', 'user', 'acknowledged_version']
    ordering_fields = ['acknowledged_date']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

