# audit_inspection/serializers.py

from rest_framework import serializers
from .models import (
    AuditType, Audit, AuditFinding, InspectionItem, 
    InspectionChecklist, Inspection, InspectionResult,
    AuditNotification, Vessel
)


class VesselSerializer(serializers.ModelSerializer):
    """Simple serializer for the Vessel model"""
    class Meta:
        model = Vessel
        fields = ['id', 'name', 'imo_number']


class AuditTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditType
        fields = ['id', 'name', 'description', 'frequency_days', 'is_mandatory']


class AuditFindingSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.ReadOnlyField(source='assigned_to.get_full_name')
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AuditFinding
        fields = [
            'id', 'audit', 'description', 'severity', 'status',
            'due_date', 'assigned_to', 'assigned_to_name', 'corrective_action',
            'closed_date', 'attachments', 'created_at', 'updated_at', 'is_overdue'
        ]


class AuditSerializer(serializers.ModelSerializer):
    findings = AuditFindingSerializer(many=True, read_only=True)
    auditor_name = serializers.ReadOnlyField(source='auditor.get_full_name')
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    audit_type_name = serializers.ReadOnlyField(source='audit_type.name')
    vessel_name = serializers.ReadOnlyField(source='vessel.name')
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Audit
        fields = [
            'id', 'audit_type', 'audit_type_name', 'planned_date', 
            'actual_date', 'auditor', 'auditor_name', 'vessel', 'vessel_name', 
            'status', 'report_file', 'comments', 'created_at', 'updated_at',
            'created_by', 'created_by_name', 'findings', 'is_overdue'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set the created_by field to the current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class InspectionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionItem
        fields = [
            'id', 'category', 'name', 'description', 
            'is_mandatory', 'regulation_reference'
        ]


class InspectionChecklistSerializer(serializers.ModelSerializer):
    items = InspectionItemSerializer(many=True, read_only=True)
    item_ids = serializers.PrimaryKeyRelatedField(
        queryset=InspectionItem.objects.all(),
        many=True,
        write_only=True,
        source='items',
        required=False
    )
    
    class Meta:
        model = InspectionChecklist
        fields = ['id', 'name', 'description', 'items', 'item_ids', 'is_active']


class InspectionResultSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    item_category = serializers.ReadOnlyField(source='item.category')
    
    class Meta:
        model = InspectionResult
        fields = [
            'id', 'inspection', 'item', 'item_name', 'item_category',
            'result', 'comments', 'evidence_file'
        ]


class InspectionSerializer(serializers.ModelSerializer):
    results = InspectionResultSerializer(many=True, read_only=True)
    inspector_name = serializers.ReadOnlyField(source='inspector.get_full_name')
    created_by_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    checklist_name = serializers.ReadOnlyField(source='checklist.name')
    vessel_name = serializers.ReadOnlyField(source='vessel.name')
    
    class Meta:
        model = Inspection
        fields = [
            'id', 'checklist', 'checklist_name', 'vessel', 'vessel_name',
            'inspector', 'inspector_name', 'planned_date', 'actual_date',
            'status', 'comments', 'report_file', 'created_at', 'updated_at',
            'created_by', 'created_by_name', 'results'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set the created_by field to the current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AuditNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditNotification
        fields = [
            'id', 'audit', 'finding', 'notification_type',
            'message', 'recipients', 'is_sent', 'sent_date', 'created_at'
        ]
        read_only_fields = ['is_sent', 'sent_date', 'created_at']
