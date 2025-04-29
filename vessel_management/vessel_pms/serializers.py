from rest_framework import serializers
from .models import Equipment, MaintenanceTask, MaintenanceHistory
from django.utils import timezone

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class MaintenanceTaskSerializer(serializers.ModelSerializer):
    days_until_due = serializers.SerializerMethodField()
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceTask
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'days_until_due', 'equipment_name', 'is_overdue']
    
    def get_days_until_due(self, obj):
        return obj.days_until_due()
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()
    
    def validate(self, data):
        """
        Validate maintenance task data
        """
        if 'next_due_date' in data and data['next_due_date'] < timezone.now():
            raise serializers.ValidationError("Next due date cannot be in the past")
        
        if 'interval_type' in data and data['interval_type'] == 'running_hours' and data.get('interval_value', 0) <= 0:
            raise serializers.ValidationError("Running hours interval must be greater than zero")
        
        return data


class MaintenanceHistorySerializer(serializers.ModelSerializer):
    completed_by_name = serializers.CharField(source='completed_by.username', read_only=True)
    task_name = serializers.CharField(source='task.task_name', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    
    class Meta:
        model = MaintenanceHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'task_name', 'equipment_name', 'completed_by_name']
    
    def create(self, validated_data):
        # Auto-assign the related equipment from the task
        if 'task' in validated_data and 'equipment' not in validated_data:
            validated_data['equipment'] = validated_data['task'].equipment
        
        # Create the history record
        history = MaintenanceHistory.objects.create(**validated_data)
        
        # Update the related task's last_completed_date and next_due_date
        task = history.task
        task.last_completed_date = history.completed_date
        task.next_due_date = task.calculate_next_due_date()
        task.status = 'scheduled'  # Reset to scheduled for the next cycle
        task.save()
        
        return history


class MaintenanceTaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = MaintenanceTask
        fields = ['id', 'task_name', 'equipment_id', 'equipment_name', 'next_due_date', 
                  'status', 'days_until_due', 'responsible_role']
    
    def get_days_until_due(self, obj):
        return obj.days_until_due()