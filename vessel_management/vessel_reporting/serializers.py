from rest_framework import serializers
from .models import Report, SavedReport, ReportSchedule, DashboardMetric

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date', 'updated_date']


class SavedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedReport
        fields = '__all__'
        read_only_fields = ['generated_by', 'generated_date']


class ReportScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSchedule
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date', 'last_run']


class DashboardMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardMetric
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date', 'last_calculated', 'last_value'] 