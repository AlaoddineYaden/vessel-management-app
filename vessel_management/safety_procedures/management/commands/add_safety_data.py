from django.core.management.base import BaseCommand
from django.utils import timezone
from safety_procedures.models import ProcedureCategory, Procedure, ProcedureVersion, ProcedureReview
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample safety procedures data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding safety procedures data...')

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        ProcedureReview.objects.all().delete()
        ProcedureVersion.objects.all().delete()
        Procedure.objects.all().delete()
        ProcedureCategory.objects.all().delete()
        self.stdout.write('Existing data cleared')

        # Get or create a system user for procedures
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
            self.stdout.write('Created system user for procedures')

        # Create procedure categories
        categories = [
            {
                'name': 'Safety Management',
                'code': 'SM',
                'description': 'Safety management system procedures',
                'order': 1
            },
            {
                'name': 'Emergency Response',
                'code': 'ER',
                'description': 'Emergency response procedures',
                'order': 2
            },
            {
                'name': 'Navigation',
                'code': 'NAV',
                'description': 'Navigation and bridge procedures',
                'order': 3
            },
            {
                'name': 'Engine Room',
                'code': 'ENG',
                'description': 'Engine room operations and maintenance',
                'order': 4
            }
        ]

        created_categories = {}
        for cat_data in categories:
            category = ProcedureCategory.objects.create(**cat_data)
            created_categories[cat_data['code']] = category
            self.stdout.write(f'Created category: {category.name}')

        # Create procedures
        today = timezone.now()
        procedures = [
            {
                'title': 'Safety Management System Manual',
                'document_type': 'MANUAL',
                'category': created_categories['SM'],
                'content': 'This manual outlines the vessel\'s safety management system...',
                'version': '1.0',
                'created_by': system_user,
                'last_reviewed_date': today - timedelta(days=180),
                'next_review_date': today + timedelta(days=180),
                'review_status': 'CURRENT',
                'review_interval_months': 12,
                'is_active': True,
                'tags': 'safety,management,system'
            },
            {
                'title': 'Emergency Response Plan',
                'document_type': 'PROCEDURE',
                'category': created_categories['ER'],
                'content': 'Procedures for responding to various emergency situations...',
                'version': '2.1',
                'created_by': system_user,
                'last_reviewed_date': today - timedelta(days=30),
                'next_review_date': today + timedelta(days=330),
                'review_status': 'CURRENT',
                'review_interval_months': 12,
                'is_active': True,
                'tags': 'emergency,response,plan'
            },
            {
                'title': 'Bridge Watchkeeping Checklist',
                'document_type': 'CHECKLIST',
                'category': created_categories['NAV'],
                'content': 'Daily checklist for bridge watchkeeping duties...',
                'version': '1.2',
                'created_by': system_user,
                'last_reviewed_date': today - timedelta(days=60),
                'next_review_date': today + timedelta(days=300),
                'review_status': 'CURRENT',
                'review_interval_months': 12,
                'is_active': True,
                'tags': 'bridge,watchkeeping,checklist'
            },
            {
                'title': 'Engine Room Maintenance Schedule',
                'document_type': 'PROCEDURE',
                'category': created_categories['ENG'],
                'content': 'Schedule and procedures for engine room maintenance...',
                'version': '3.0',
                'created_by': system_user,
                'last_reviewed_date': today - timedelta(days=90),
                'next_review_date': today + timedelta(days=270),
                'review_status': 'CURRENT',
                'review_interval_months': 12,
                'is_active': True,
                'tags': 'engine,maintenance,schedule'
            }
        ]

        for proc_data in procedures:
            try:
                procedure = Procedure.objects.create(**proc_data)
                self.stdout.write(f'Created procedure: {procedure.title}')

                # Create version history
                version = ProcedureVersion.objects.create(
                    procedure=procedure,
                    version=procedure.version,
                    created_by=system_user,
                    change_notes='Initial version'
                )
                self.stdout.write(f'Created version: {version.version} for {procedure.title}')

                # Create review record
                review = ProcedureReview.objects.create(
                    procedure=procedure,
                    reviewed_by=system_user,
                    comments='Initial review completed',
                    changes_required=False,
                    approved=True
                )
                self.stdout.write(f'Created review for {procedure.title}')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating procedure {proc_data["title"]}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded safety procedures data')) 