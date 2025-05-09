# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from vessel_pms.models import Equipment, MaintenanceTask, MaintenanceHistory
from core.models import Vessel
from django.contrib.auth import get_user_model
from datetime import timedelta
import random
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Seeds the database with sample maintenance data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding maintenance data...')
        
        try:
            # Get or create a system user
            User = get_user_model()
            system_user = User.objects.filter(is_superuser=True).first()
            if not system_user:
                system_user = User.objects.create_superuser(
                    username='system',
                    email='system@example.com',
                    password='system123'
                )
            self.stdout.write('System user created/retrieved successfully')

            # Get a vessel to assign equipment to
            vessel = Vessel.objects.first()
            if not vessel:
                self.stdout.write(self.style.ERROR('No vessels found in the database. Please create a vessel first.'))
                return
            self.stdout.write(f'Using vessel: {vessel.name}')

            # Sample equipment data
            equipment_data = [
                {
                    'name': 'Main Engine',
                    'model': 'MAN B&W 6S50MC-C',
                    'serial_number': 'ME-001',
                    'manufacturer': 'MAN Energy Solutions',
                    'installation_date': timezone.now().date() - timedelta(days=365*2),
                    'location': 'Engine Room',
                    'status': 'operational',
                    'vessel': vessel
                },
                {
                    'name': 'Auxiliary Engine',
                    'model': 'Caterpillar 3516B',
                    'serial_number': 'AE-001',
                    'manufacturer': 'Caterpillar',
                    'installation_date': timezone.now().date() - timedelta(days=365*3),
                    'location': 'Engine Room',
                    'status': 'operational',
                    'vessel': vessel
                },
                {
                    'name': 'Fresh Water Generator',
                    'model': 'Alfa Laval S10',
                    'serial_number': 'FWG-001',
                    'manufacturer': 'Alfa Laval',
                    'installation_date': timezone.now().date() - timedelta(days=365),
                    'location': 'Engine Room',
                    'status': 'operational',
                    'vessel': vessel
                },
                {
                    'name': 'Boiler',
                    'model': 'SAACKE SKVJ 2000',
                    'serial_number': 'BLR-001',
                    'manufacturer': 'SAACKE',
                    'installation_date': timezone.now().date() - timedelta(days=365*4),
                    'location': 'Engine Room',
                    'status': 'maintenance',
                    'vessel': vessel
                }
            ]

            # Create equipment
            equipment_objects = []
            for data in equipment_data:
                try:
                    equipment = Equipment.objects.create(**data)
                    equipment_objects.append(equipment)
                    self.stdout.write(f'Created equipment: {equipment}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating equipment {data["name"]}: {str(e)}'))
                    raise

            # Sample maintenance tasks
            maintenance_tasks = [
                {
                    'task_name': 'Engine Oil Change',
                    'description': 'Change main engine oil and filters',
                    'interval_type': 'running_hours',
                    'interval_value': 500,
                    'responsible_role': 'Chief Engineer',
                    'instructions': '1. Drain old oil\n2. Replace filters\n3. Fill with new oil\n4. Check oil pressure',
                    'next_due_date': timezone.now() + timedelta(days=30)
                },
                {
                    'task_name': 'Cooling Water Treatment',
                    'description': 'Check and treat cooling water system',
                    'interval_type': 'monthly',
                    'interval_value': 1,
                    'responsible_role': '2nd Engineer',
                    'instructions': '1. Check water quality\n2. Add treatment chemicals\n3. Record readings',
                    'next_due_date': timezone.now() + timedelta(days=15)
                },
                {
                    'task_name': 'Boiler Inspection',
                    'description': 'Annual boiler inspection and cleaning',
                    'interval_type': 'annual',
                    'interval_value': 1,
                    'responsible_role': 'Chief Engineer',
                    'instructions': '1. Shut down boiler\n2. Open inspection ports\n3. Clean tubes\n4. Check safety devices',
                    'next_due_date': timezone.now() + timedelta(days=60)
                }
            ]

            # Create maintenance tasks
            for equipment in equipment_objects:
                for task_data in maintenance_tasks:
                    try:
                        task = MaintenanceTask.objects.create(
                            equipment=equipment,
                            **task_data
                        )
                        self.stdout.write(f'Created maintenance task: {task}')
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating task {task_data["task_name"]} for {equipment}: {str(e)}'))
                        raise

            # Sample maintenance history
            for equipment in equipment_objects:
                for task in equipment.maintenance_tasks.all():
                    try:
                        # Create 2-3 historical records per task
                        for _ in range(random.randint(2, 3)):
                            completed_date = timezone.now() - timedelta(days=random.randint(30, 365))
                            history = MaintenanceHistory.objects.create(
                                task=task,
                                equipment=equipment,
                                completed_by=system_user,
                                completed_date=completed_date,
                                remarks=f'Routine maintenance completed successfully',
                                running_hours=random.randint(1000, 5000),
                                parts_used='Various consumables',
                                duration=random.randint(60, 240)
                            )
                            self.stdout.write(f'Created maintenance history: {history}')
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating history for task {task} on {equipment}: {str(e)}'))
                        raise

            self.stdout.write(self.style.SUCCESS('Successfully seeded maintenance data'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding data: {str(e)}'))
            raise 