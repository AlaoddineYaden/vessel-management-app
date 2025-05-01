from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from safety_procedures.models import (
    ProcedureCategory,
    Procedure,
    ProcedureVersion,
    ProcedureReview,
    ProcedureAcknowledgment
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample Safety Procedures & ISM Manuals data'

    def handle(self, *args, **options):
        # Create or get admin user
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )

        # Sample procedure categories
        CATEGORIES = [
            {
                'code': 'ISM',
                'name': 'ISM Manual',
                'description': 'International Safety Management Code procedures',
                'order': 1
            },
            {
                'code': 'SAF',
                'name': 'Safety',
                'description': 'General safety procedures',
                'order': 2
            },
            {
                'code': 'EMG',
                'name': 'Emergency',
                'description': 'Emergency response procedures',
                'order': 3
            },
            {
                'code': 'OPS',
                'name': 'Operations',
                'description': 'Operational procedures',
                'order': 4
            },
            {
                'code': 'ENV',
                'name': 'Environmental',
                'description': 'Environmental protection procedures',
                'order': 5
            }
        ]

        # Create categories
        categories = {}
        for cat_data in CATEGORIES:
            category, created = ProcedureCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults=cat_data
            )
            categories[cat_data['code']] = category
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )

        # Sample procedures
        PROCEDURES = [
            {
                'title': 'Safety Management System Manual',
                'document_type': 'MANUAL',
                'category': 'ISM',
                'content': 'This manual outlines the company\'s Safety Management System (SMS) in accordance with the ISM Code.',
                'version': '1.0',
                'review_interval_months': 12,
                'tags': 'ISM, SMS, Manual'
            },
            {
                'title': 'Emergency Response Plan',
                'document_type': 'PROCEDURE',
                'category': 'EMG',
                'content': 'Detailed procedures for responding to various emergency situations onboard.',
                'version': '2.1',
                'review_interval_months': 6,
                'tags': 'Emergency, Response, Safety'
            },
            {
                'title': 'Fire Prevention and Control',
                'document_type': 'PROCEDURE',
                'category': 'SAF',
                'content': 'Procedures for fire prevention, detection, and control onboard.',
                'version': '3.0',
                'review_interval_months': 6,
                'tags': 'Fire, Safety, Prevention'
            },
            {
                'title': 'Ballast Water Management',
                'document_type': 'PROCEDURE',
                'category': 'ENV',
                'content': 'Procedures for managing ballast water in compliance with environmental regulations.',
                'version': '1.2',
                'review_interval_months': 12,
                'tags': 'Ballast, Environment, Compliance'
            },
            {
                'title': 'Navigation Bridge Procedures',
                'document_type': 'PROCEDURE',
                'category': 'OPS',
                'content': 'Standard operating procedures for the navigation bridge.',
                'version': '2.0',
                'review_interval_months': 12,
                'tags': 'Navigation, Bridge, Operations'
            }
        ]

        # Create procedures
        procedures_created = 0
        reviews_created = 0
        acknowledgments_created = 0

        for proc_data in PROCEDURES:
            procedure, created = Procedure.objects.get_or_create(
                title=proc_data['title'],
                defaults={
                    'document_type': proc_data['document_type'],
                    'category': categories[proc_data['category']],
                    'content': proc_data['content'],
                    'version': proc_data['version'],
                    'created_by': admin_user,
                    'review_interval_months': proc_data['review_interval_months'],
                    'tags': proc_data['tags'],
                    'review_status': 'CURRENT',
                    'last_reviewed_date': timezone.now() - timedelta(days=30),
                    'next_review_date': timezone.now() + timedelta(days=30),
                    'is_active': True
                }
            )

            if created:
                procedures_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created procedure: {procedure.title}')
                )

                # Create version history
                version = ProcedureVersion.objects.create(
                    procedure=procedure,
                    version=procedure.version,
                    created_by=admin_user,
                    change_notes='Initial version'
                )

                # Create review
                review = ProcedureReview.objects.create(
                    procedure=procedure,
                    reviewed_by=admin_user,
                    comments='Initial review completed',
                    changes_required=False,
                    approved=True
                )
                reviews_created += 1

                # Create acknowledgment
                acknowledgment = ProcedureAcknowledgment.objects.create(
                    procedure=procedure,
                    user=admin_user,
                    acknowledged_version=procedure.version,
                    comments='Acknowledged and understood'
                )
                acknowledgments_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'- {procedures_created} procedures\n'
                f'- {reviews_created} reviews\n'
                f'- {acknowledgments_created} acknowledgments'
            )
        ) 