from rest_framework import serializers
from .models import NonConformity, CorrectiveAction, EvidenceFile, PreventiveAction

class EvidenceFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceFile
        fields = ['id', 'file', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class CorrectiveActionSerializer(serializers.ModelSerializer):
    evidence_files = EvidenceFileSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CorrectiveAction
        fields = ['id', 'non_conformity', 'description', 'assigned_to', 'due_date', 
                  'completed_date', 'verification_status', 'verification_comments', 
                  'evidence_files', 'is_overdue', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class PreventiveActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreventiveAction
        fields = ['id', 'non_conformity', 'description', 'assigned_to', 'due_date', 
                  'status', 'completed_date', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class NonConformitySerializer(serializers.ModelSerializer):
    corrective_actions = CorrectiveActionSerializer(many=True, read_only=True)
    preventive_actions = PreventiveActionSerializer(many=True, read_only=True)
    
    class Meta:
        model = NonConformity
        fields = ['id', 'description', 'detection_date', 'source_type', 'source_id', 
                  'severity', 'vessel_id', 'status', 'root_cause', 'reference_documents', 
                  'corrective_actions', 'preventive_actions', 'created_by',
                  'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']
