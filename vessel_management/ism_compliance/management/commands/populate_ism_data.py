from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from ism_compliance.models import ISMRequirement, ComplianceItem, ComplianceReview
from core.models import Vessel
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample ISM Compliance data'

    def handle(self, *args, **options):
        # Sample ISM requirements
        ISM_REQUIREMENTS = [
            {
                'ism_section': '1',
                'requirement_code': '1.1',
                'requirement_text': 'The Company should establish safety and environmental protection policy',
                'guidance_notes': 'Policy should be documented and communicated to all personnel',
            },
            {
                'ism_section': '1',
                'requirement_code': '1.2',
                'requirement_text': 'The Company should ensure that the policy is implemented and maintained',
                'guidance_notes': 'Regular reviews and updates of the policy are required',
            },
            {
                'ism_section': '5',
                'requirement_code': '5.1',
                'requirement_text': 'The Company should clearly define and document the master\'s responsibility',
                'guidance_notes': 'Master\'s responsibilities should be clearly defined in the SMS',
            },
            {
                'ism_section': '5',
                'requirement_code': '5.2',
                'requirement_text': 'The Company should ensure that the master is properly qualified',
                'guidance_notes': 'Verify master\'s certificates and experience',
            },
            {
                'ism_section': '6',
                'requirement_code': '6.1',
                'requirement_text': 'The Company should ensure that each ship is manned with qualified, certificated and medically fit seafarers',
                'guidance_notes': 'Verify crew certificates and medical fitness',
            },
            {
                'ism_section': '6',
                'requirement_code': '6.2',
                'requirement_text': 'The Company should establish procedures to ensure that new personnel are given proper familiarization',
                'guidance_notes': 'Document familiarization procedures and records',
            },
            {
                'ism_section': '7',
                'requirement_code': '7.1',
                'requirement_text': 'The Company should establish procedures for the preparation of plans and instructions for key shipboard operations',
                'guidance_notes': 'Ensure all critical operations are documented',
            },
            {
                'ism_section': '8',
                'requirement_code': '8.1',
                'requirement_text': 'The Company should establish procedures to identify, describe and respond to potential emergency shipboard situations',
                'guidance_notes': 'Emergency procedures should be documented and practiced',
            },
            {
                'ism_section': '10',
                'requirement_code': '10.1',
                'requirement_text': 'The Company should establish procedures to ensure that the ship is maintained in conformity with the provisions of the relevant rules and regulations',
                'guidance_notes': 'Maintenance procedures should be documented and followed',
            },
            {
                'ism_section': '10',
                'requirement_code': '10.2',
                'requirement_text': 'The Company should ensure that inspections are held at appropriate intervals',
                'guidance_notes': 'Regular inspections should be scheduled and documented',
            },
        ]

        # Create ISM requirements
        requirements_created = 0
        for req_data in ISM_REQUIREMENTS:
            requirement, created = ISMRequirement.objects.get_or_create(
                requirement_code=req_data['requirement_code'],
                defaults=req_data
            )
            if created:
                requirements_created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created ISM requirement: {requirement.requirement_code}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {requirements_created} ISM requirements'
            )
        )

        # Get or create a user for assessments
        user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )

        # Create compliance items for each vessel
        vessels = Vessel.objects.all()
        compliance_items_created = 0
        reviews_created = 0

        for vessel in vessels:
            for requirement in ISMRequirement.objects.all():
                # Create compliance item
                item, created = ComplianceItem.objects.get_or_create(
                    vessel_id=vessel.id,
                    ism_requirement=requirement,
                    defaults={
                        'compliance_status': 'compliant' if requirement.ism_section in ['1', '2'] else 'pending_review',
                        'risk_level': 'high' if requirement.ism_section in ['5', '6', '7', '8', '10'] else 'medium',
                        'assessment_date': timezone.now() - timedelta(days=30),
                        'next_review_date': timezone.now() + timedelta(days=30),
                        'comments': f'Initial assessment for {vessel.name}',
                        'assessor': user,
                    }
                )

                if created:
                    compliance_items_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created compliance item for {vessel.name} - {requirement.requirement_code}'
                        )
                    )

                    # Create review for the compliance item
                    review = ComplianceReview.objects.create(
                        compliance_item=item,
                        scheduled_date=timezone.now() + timedelta(days=30),
                        status='scheduled',
                        reviewer=user,
                        findings='Initial review scheduled',
                        recommendations='Regular monitoring required'
                    )
                    reviews_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created review for {vessel.name} - {requirement.requirement_code}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {compliance_items_created} compliance items and {reviews_created} reviews'
            )
        ) 