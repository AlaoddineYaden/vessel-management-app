from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from nc_module.models import NonConformity, CorrectiveAction, PreventiveAction

class Command(BaseCommand):
    help = 'Populates the database with sample non-conformity data'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Create admin user if not exists
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        # Sample non-conformities data
        sample_nonconformities = [
            {
                'description': 'Safety equipment not properly stored in designated area',
                'source_type': 'INSPECTION',
                'severity': 'MEDIUM',
                'vessel_id': 1,
                'root_cause': 'Lack of proper storage procedures and training',
                'reference_documents': 'Safety Management System Manual, Section 4.2'
            },
            {
                'description': 'Fire extinguisher inspection overdue by 2 months',
                'source_type': 'AUDIT',
                'severity': 'HIGH',
                'vessel_id': 1,
                'root_cause': 'Inadequate maintenance scheduling system',
                'reference_documents': 'Maintenance Management System, Fire Safety Procedures'
            },
            {
                'description': 'Crew member injured during cargo operations',
                'source_type': 'INCIDENT',
                'severity': 'CRITICAL',
                'vessel_id': 2,
                'root_cause': 'Inadequate risk assessment and supervision',
                'reference_documents': 'Cargo Operations Manual, Risk Assessment Procedures'
            },
            {
                'description': 'Oil spill detected in engine room',
                'source_type': 'INSPECTION',
                'severity': 'HIGH',
                'vessel_id': 2,
                'root_cause': 'Faulty equipment and lack of containment measures',
                'reference_documents': 'Environmental Management Plan, Oil Spill Response Procedures'
            },
            {
                'description': 'Navigation equipment calibration overdue',
                'source_type': 'AUDIT',
                'severity': 'MEDIUM',
                'vessel_id': 3,
                'root_cause': 'Inadequate maintenance tracking system',
                'reference_documents': 'Navigation Equipment Manual, Maintenance Schedule'
            }
        ]

        # Create non-conformities
        nonconformities = []
        for nc_data in sample_nonconformities:
            nc = NonConformity.objects.create(
                **nc_data,
                detection_date=timezone.now().date() - timedelta(days=random.randint(1, 30)),
                created_by=admin_user
            )
            nonconformities.append(nc)
            self.stdout.write(self.style.SUCCESS(f'Created non-conformity: {nc}'))

        # Sample corrective actions
        corrective_actions = [
            {
                'description': 'Implement proper storage procedures and conduct training',
                'due_date': timezone.now().date() + timedelta(days=7)
            },
            {
                'description': 'Update maintenance scheduling system and conduct audit',
                'due_date': timezone.now().date() + timedelta(days=14)
            },
            {
                'description': 'Review and update risk assessment procedures',
                'due_date': timezone.now().date() + timedelta(days=10)
            },
            {
                'description': 'Install new containment measures and repair equipment',
                'due_date': timezone.now().date() + timedelta(days=5)
            },
            {
                'description': 'Update maintenance tracking system and conduct calibration',
                'due_date': timezone.now().date() + timedelta(days=3)
            }
        ]

        # Create corrective actions
        for nc, ca_data in zip(nonconformities, corrective_actions):
            ca = CorrectiveAction.objects.create(
                non_conformity=nc,
                **ca_data,
                assigned_to=admin_user
            )
            self.stdout.write(self.style.SUCCESS(f'Created corrective action: {ca}'))

        # Sample preventive actions
        preventive_actions = [
            {
                'description': 'Implement regular safety equipment audits',
                'due_date': timezone.now().date() + timedelta(days=30)
            },
            {
                'description': 'Develop automated maintenance tracking system',
                'due_date': timezone.now().date() + timedelta(days=60)
            },
            {
                'description': 'Enhance crew training program for cargo operations',
                'due_date': timezone.now().date() + timedelta(days=45)
            },
            {
                'description': 'Install automated oil spill detection system',
                'due_date': timezone.now().date() + timedelta(days=90)
            },
            {
                'description': 'Implement digital maintenance management system',
                'due_date': timezone.now().date() + timedelta(days=75)
            }
        ]

        # Create preventive actions
        for nc, pa_data in zip(nonconformities, preventive_actions):
            pa = PreventiveAction.objects.create(
                non_conformity=nc,
                **pa_data,
                assigned_to=admin_user
            )
            self.stdout.write(self.style.SUCCESS(f'Created preventive action: {pa}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated NC Module with sample data')) 