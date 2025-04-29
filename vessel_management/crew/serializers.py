# crew/serializers.py
from rest_framework import serializers
from .models import Crew, CrewCertificate, CrewAssignment, Vessel, CertificateNotification


class CrewCertificateSerializer(serializers.ModelSerializer):
    days_until_expiry = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = CrewCertificate
        fields = [
            'id', 'crew', 'certificate_type', 'certificate_name',
            'certificate_number', 'issue_date', 'expiry_date',
            'issuing_authority', 'document_file', 'notes',
            'days_until_expiry', 'is_expired', 'created_at', 'updated_at'
        ]
    
    def get_days_until_expiry(self, obj):
        return obj.days_until_expiry()
    
    def get_is_expired(self, obj):
        return obj.is_expired()


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = [
            'id', 'name', 'rank', 'nationality', 'date_of_birth',
            'passport_number', 'seaman_book_number', 'phone_number',
            'email', 'address', 'emergency_contact_name',
            'emergency_contact_phone', 'medical_information',
            'notes', 'is_active', 'created_at', 'updated_at'
        ]


class CrewDetailSerializer(serializers.ModelSerializer):
    certificates = CrewCertificateSerializer(many=True, read_only=True)
    active_certificates = serializers.SerializerMethodField()
    expired_certificates = serializers.SerializerMethodField()
    current_assignment = serializers.SerializerMethodField()
    
    class Meta:
        model = Crew
        fields = [
            'id', 'name', 'rank', 'nationality', 'date_of_birth',
            'passport_number', 'seaman_book_number', 'phone_number',
            'email', 'address', 'emergency_contact_name',
            'emergency_contact_phone', 'medical_information',
            'notes', 'is_active', 'created_at', 'updated_at',
            'certificates', 'active_certificates', 'expired_certificates',
            'current_assignment'
        ]
    
    def get_active_certificates(self, obj):
        active_certs = obj.get_active_certificates()
        return CrewCertificateSerializer(active_certs, many=True).data
    
    def get_expired_certificates(self, obj):
        expired_certs = obj.get_expired_certificates()
        return CrewCertificateSerializer(expired_certs, many=True).data
    
    def get_current_assignment(self, obj):
        current_assignments = obj.assignments.filter(is_current=True).first()
        if current_assignments:
            return CrewAssignmentSerializer(current_assignments).data
        return None


class VesselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vessel
        fields = ['id', 'name', 'imo_number', 'vessel_type']
        ref_name = "CrewVessel"


class CrewAssignmentSerializer(serializers.ModelSerializer):
    vessel_name = serializers.ReadOnlyField(source='vessel.name')
    crew_name = serializers.ReadOnlyField(source='crew.name')
    
    class Meta:
        model = CrewAssignment
        fields = [
            'id', 'crew', 'crew_name', 'vessel', 'vessel_name',
            'rank', 'start_date', 'end_date', 'is_current',
            'notes', 'created_at', 'updated_at'
        ]


class CertificateNotificationSerializer(serializers.ModelSerializer):
    crew_name = serializers.ReadOnlyField(source='certificate.crew.name')
    certificate_name = serializers.ReadOnlyField(source='certificate.certificate_name')
    expiry_date = serializers.ReadOnlyField(source='certificate.expiry_date')
    
    class Meta:
        model = CertificateNotification
        fields = [
            'id', 'certificate', 'certificate_name', 'crew_name',
            'expiry_date', 'notification_date', 'days_before_expiry',
            'status', 'message', 'sent_to', 'acknowledged_by',
            'acknowledged_at'
        ]
        read_only_fields = ['notification_date']