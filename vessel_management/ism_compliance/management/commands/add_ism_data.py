from django.core.management.base import BaseCommand
from django.utils import timezone
from ism_compliance.models import ISMRequirement, ComplianceItem, ComplianceEvidence, ComplianceReview
from core.models import Vessel
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample ISM compliance data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding ISM compliance data...')

        # Get the vessel
        vessel = Vessel.objects.first()
        if not vessel:
            self.stdout.write(self.style.ERROR('No vessels found in the database. Please create a vessel first.'))
            return

        # Get or create a system user
        system_user, created = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            system_user.set_password('system123')
            system_user.save()
            self.stdout.write('Created system user for ISM data')

        # Create ISM requirements
        requirements = [
            {
                'ism_section': '1',
                'requirement_code': '1.1.1',
                'requirement_text': 'The Company should establish, implement and maintain a safety management system',
                'guidance_notes': 'This is the fundamental requirement for ISM implementation'
            },
            {
                'ism_section': '2',
                'requirement_code': '2.1.1',
                'requirement_text': 'The Company should establish a safety and environmental protection policy',
                'guidance_notes': 'Policy should be documented and communicated to all personnel'
            },
            {
                'ism_section': '3',
                'requirement_code': '3.1.1',
                'requirement_text': 'The Company should define and document the responsibility, authority and interrelation of all personnel',
                'guidance_notes': 'Organizational structure should be clearly defined'
            },
            {
                'ism_section': '4',
                'requirement_code': '4.1.1',
                'requirement_text': 'The Company should designate a person or persons ashore having direct access to the highest level of management',
                'guidance_notes': 'DPA should be appointed and their role documented'
            }
        ]

        created_requirements = {}
        for req_data in requirements:
            requirement = ISMRequirement.objects.create(**req_data)
            created_requirements[req_data['requirement_code']] = requirement
            self.stdout.write(f'Created ISM requirement: {requirement.requirement_code}')

        # Create compliance items
        today = timezone.now()
        compliance_items = [
            {
                'ism_requirement': created_requirements['1.1.1'],
                'vessel': vessel,
                'compliance_status': 'compliant',
                'risk_level': 'low',
                'assessment_date': today - timedelta(days=30),
                'next_review_date': today + timedelta(days=330),
                'assessor': system_user,
                'comments': 'SMS is well established and maintained'
            },
            {
                'ism_requirement': created_requirements['2.1.1'],
                'vessel': vessel,
                'compliance_status': 'compliant',
                'risk_level': 'low',
                'assessment_date': today - timedelta(days=30),
                'next_review_date': today + timedelta(days=330),
                'assessor': system_user,
                'comments': 'Safety policy is documented and communicated'
            },
            {
                'ism_requirement': created_requirements['3.1.1'],
                'vessel': vessel,
                'compliance_status': 'partially_compliant',
                'risk_level': 'medium',
                'assessment_date': today - timedelta(days=30),
                'next_review_date': today + timedelta(days=180),
                'assessor': system_user,
                'comments': 'Some organizational roles need better documentation'
            },
            {
                'ism_requirement': created_requirements['4.1.1'],
                'vessel': vessel,
                'compliance_status': 'compliant',
                'risk_level': 'low',
                'assessment_date': today - timedelta(days=30),
                'next_review_date': today + timedelta(days=330),
                'assessor': system_user,
                'comments': 'DPA is appointed and accessible'
            }
        ]

        for item_data in compliance_items:
            try:
                item = ComplianceItem.objects.create(**item_data)
                self.stdout.write(f'Created compliance item for {item.ism_requirement.requirement_code}')

                # Create evidence
                evidence = ComplianceEvidence.objects.create(
                    compliance_item=item,
                    title=f'Evidence for {item.ism_requirement.requirement_code}',
                    description=f'Supporting documentation for {item.ism_requirement.requirement_code}',
                    evidence_type='document',
                    uploaded_by=system_user
                )
                self.stdout.write(f'Created evidence for {item.ism_requirement.requirement_code}')

                # Create review
                review = ComplianceReview.objects.create(
                    compliance_item=item,
                    scheduled_date=today + timedelta(days=30),
                    reviewer=system_user,
                    status='scheduled',
                    findings='Initial review scheduled',
                    recommendations='Regular monitoring required'
                )
                self.stdout.write(f'Created review for {item.ism_requirement.requirement_code}')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating compliance item: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded ISM compliance data')) 