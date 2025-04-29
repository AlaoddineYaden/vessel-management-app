from rest_framework import serializers
from .models import ProcedureCategory, Procedure, ProcedureVersion, ProcedureReview, ProcedureAcknowledgment


class ProcedureCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureCategory
        fields = '__all__'


class ProcedureReviewSerializer(serializers.ModelSerializer):
    reviewed_by_name = serializers.ReadOnlyField(source='reviewed_by.get_full_name')
    
    class Meta:
        model = ProcedureReview
        fields = ['id', 'review_date', 'reviewed_by', 'reviewed_by_name', 
                 'comments', 'changes_required', 'approved']
        read_only_fields = ['review_date']


class ProcedureVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    
    class Meta:
        model = ProcedureVersion
        fields = ['id', 'version', 'created_date', 'created_by', 
                 'created_by_name', 'change_notes']
        read_only_fields = ['created_date']


class ProcedureAcknowledgmentSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    
    class Meta:
        model = ProcedureAcknowledgment
        fields = ['id', 'user', 'user_name', 'acknowledged_date', 
                 'acknowledged_version', 'comments']
        read_only_fields = ['acknowledged_date']


class ProcedureSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    acknowledgment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Procedure
        fields = ['id', 'title', 'document_type', 'category', 'category_name', 
                 'content', 'file_upload', 'version', 'created_date', 
                 'created_by', 'created_by_name', 'last_reviewed_date', 
                 'next_review_date', 'review_status', 'review_interval_months', 
                 'is_active', 'tags', 'acknowledgment_count']
        read_only_fields = ['created_date', 'review_status']
    
    def get_acknowledgment_count(self, obj):
        return obj.acknowledgments.filter(acknowledged_version=obj.version).count()


class ProcedureDetailSerializer(ProcedureSerializer):
    reviews = ProcedureReviewSerializer(many=True, read_only=True)
    versions = ProcedureVersionSerializer(many=True, read_only=True)
    acknowledgments = ProcedureAcknowledgmentSerializer(many=True, read_only=True)
    
    class Meta(ProcedureSerializer.Meta):
        fields = ProcedureSerializer.Meta.fields + ['reviews', 'versions', 'acknowledgments']

