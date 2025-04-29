from rest_framework import serializers
from django.utils import timezone
from .models import ISMRequirement, ComplianceItem, ComplianceEvidence, ComplianceReview


class ISMRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ISMRequirement
        fields = '__all__'


class ComplianceEvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceEvidence
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'upload_date']
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['uploaded_by'] = request.user
        return super().create(validated_data)


class ComplianceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceReview
        fields = '__all__'
        read_only_fields = ['reviewer', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['reviewer'] = request.user
        return super().create(validated_data)


class ComplianceItemSerializer(serializers.ModelSerializer):
    evidence = ComplianceEvidenceSerializer(many=True, read_only=True)
    reviews = ComplianceReviewSerializer(many=True, read_only=True)
    ism_requirement_details = ISMRequirementSerializer(source='ism_requirement', read_only=True)
    
    class Meta:
        model = ComplianceItem
        fields = '__all__'
        read_only_fields = ['assessor', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['assessor'] = request.user
        return super().create(validated_data)


class ComplianceItemDetailSerializer(ComplianceItemSerializer):
    """Full detail serializer with nested evidence and review data"""
    class Meta(ComplianceItemSerializer.Meta):
        pass


class ComplianceItemListSerializer(ComplianceItemSerializer):
    """Summary serializer for list views"""
    class Meta(ComplianceItemSerializer.Meta):
        fields = ['id', 'ism_requirement', 'vessel_id', 'compliance_status', 
                  'risk_level', 'assessment_date', 'next_review_date']


class ComplianceReportSerializer(serializers.Serializer):
    """Serializer for generating compliance reports"""
    vessel_id = serializers.UUIDField(required=True)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(default=timezone.now)
    include_evidence = serializers.BooleanField(default=True)
    include_reviews = serializers.BooleanField(default=True)
    format = serializers.ChoiceField(choices=['json', 'pdf', 'csv'], default='json')
