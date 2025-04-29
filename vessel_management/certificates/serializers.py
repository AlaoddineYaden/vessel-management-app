# certificates/serializers.py
from rest_framework import serializers
from .models import Certificate, CertificateType, CertificateRenewal
from crew.models import Vessel  # Import the Vessel model

class CertificateTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateType
        fields = '__all__'

class CertificateRenewalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateRenewal
        fields = '__all__'
        read_only_fields = ['certificate', 'initiated_date']

class CertificateSerializer(serializers.ModelSerializer):
    days_to_expiry = serializers.SerializerMethodField()
    certificate_type_name = serializers.CharField(source='certificate_type.name', read_only=True)
    vessel_name = serializers.CharField(source='vessel.name', read_only=True)
    vessel_imo = serializers.CharField(source='vessel.imo_number', read_only=True)
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_name', 'certificate_type', 'certificate_type_name',
            'certificate_number', 'issue_date', 'expiry_date', 'issuing_authority',
            'status', 'vessel', 'vessel_name', 'vessel_imo', 'document_file', 
            'created_at', 'updated_at', 'notes', 'days_to_expiry'
        ]
        read_only_fields = ['created_at', 'updated_at', 'days_to_expiry', 'vessel_name', 'vessel_imo']
    
    def get_days_to_expiry(self, obj):
        from django.utils import timezone
        today = timezone.now().date()
        return (obj.expiry_date - today).days

class CertificateDetailSerializer(CertificateSerializer):
    renewals = CertificateRenewalSerializer(many=True, read_only=True)
    
    class Meta(CertificateSerializer.Meta):
        fields = CertificateSerializer.Meta.fields + ['renewals']
        
class CertificateUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['document_file']