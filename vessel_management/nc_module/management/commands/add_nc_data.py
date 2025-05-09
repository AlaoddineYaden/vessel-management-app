from django.core.management.base import BaseCommand
from django.utils import timezone
from nc_module.models import NonConformity, CorrectiveAction, PreventiveAction, NCHistory, NCComment, NCAttachment
from core.models import Vessel
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample non-conformity data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding non-conformity data...')

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        NCHistory.objects.all().delete()
        NCComment.objects.all().delete()
        NCAttachment.objects.all().delete()
        PreventiveAction.objects.all().delete()
        CorrectiveAction.objects.all().delete()
        NonConformity.objects.all().delete()
        self.stdout.write('Existing data cleared')

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
            self.stdout.write('Created system user for NC data')

        # Create non-conformities
        today = timezone.now().date()
        non_conformities = [
            {
                'description': 'Fire extinguisher not properly maintained',
                'detection_date': today - timedelta(days=30),
                'source_type': 'INSPECTION',
                'source_id': 'INS-2023-001',
                'severity': 'HIGH',
                'vessel': vessel,
                'status': 'IN_PROGRESS',
                'root_cause': 'Lack of regular maintenance schedule',
                'reference_documents': 'Fire Safety Inspection Report'
            },
            {
                'description': 'Incomplete engine room logbook entries',
                'detection_date': today - timedelta(days=15),
                'source_type': 'AUDIT',
                'source_id': 'AUD-2023-001',
                'severity': 'MEDIUM',
                'vessel': vessel,
                'status': 'OPEN',
                'root_cause': 'Crew training needed on logbook procedures',
                'reference_documents': 'Internal Audit Report'
            },
            {
                'description': 'Navigation equipment calibration overdue',
                'detection_date': today - timedelta(days=7),
                'source_type': 'INSPECTION',
                'source_id': 'INS-2023-002',
                'severity': 'HIGH',
                'vessel': vessel,
                'status': 'CLOSED',
                'root_cause': 'Calibration schedule not followed',
                'reference_documents': 'Navigation Equipment Inspection Report'
            }
        ]

        for nc_data in non_conformities:
            try:
                nc = NonConformity.objects.create(**nc_data)
                self.stdout.write(f'Created non-conformity: {nc.description[:50]}...')

                # Create corrective action
                corrective_action = CorrectiveAction.objects.create(
                    non_conformity=nc,
                    description=f'Corrective action for {nc.description[:50]}...',
                    assigned_to=system_user,
                    due_date=today + timedelta(days=30)
                )
                self.stdout.write(f'Created corrective action for NC-{nc.id}')

                # Create preventive action
                preventive_action = PreventiveAction.objects.create(
                    non_conformity=nc,
                    description=f'Preventive action to avoid recurrence of {nc.description[:50]}...',
                    assigned_to=system_user,
                    due_date=today + timedelta(days=45),
                    status='PENDING'
                )
                self.stdout.write(f'Created preventive action for NC-{nc.id}')

                # Create history entries
                history_entries = [
                    {
                        'action': 'CREATED',
                        'details': 'Non-conformity created'
                    },
                    {
                        'action': 'STATUS_CHANGED',
                        'details': f'Status changed to {nc.status}'
                    },
                    {
                        'action': 'ASSIGNED',
                        'details': f'Assigned to {system_user.username}'
                    }
                ]

                for entry_data in history_entries:
                    history = NCHistory.objects.create(
                        non_conformity=nc,
                        user=system_user,
                        **entry_data
                    )
                    self.stdout.write(f'Created history entry: {history.action} for NC-{nc.id}')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating non-conformity: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded non-conformity data')) 