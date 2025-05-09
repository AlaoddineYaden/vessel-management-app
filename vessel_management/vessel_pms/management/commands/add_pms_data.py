from django.core.management.base import BaseCommand
from django.utils import timezone
from vessel_pms.models import Equipment, MaintenanceTask, MaintenanceHistory
from core.models import Vessel
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample PMS data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding PMS data...')

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        MaintenanceHistory.objects.all().delete()
        MaintenanceTask.objects.all().delete()
        Equipment.objects.all().delete()
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
            self.stdout.write('Created system user for PMS')

        # Create equipment
        today = timezone.now().date()
        equipment_list = [
            {
                'name': 'Main Engine',
                'model': 'MAN B&W 6S70ME-C8.2',
                'serial_number': 'ME12345',
                'manufacturer': 'MAN Energy Solutions',
                'installation_date': today - timedelta(days=365*2),
                'location': 'Engine Room',
                'vessel': vessel,
                'status': 'operational'
            },
            {
                'name': 'Auxiliary Engine #1',
                'model': 'Wärtsilä 6L20',
                'serial_number': 'AE12346',
                'manufacturer': 'Wärtsilä',
                'installation_date': today - timedelta(days=365*2),
                'location': 'Engine Room',
                'vessel': vessel,
                'status': 'operational'
            },
            {
                'name': 'Radar System',
                'model': 'FAR-2228',
                'serial_number': 'RS12347',
                'manufacturer': 'Furuno',
                'installation_date': today - timedelta(days=365),
                'location': 'Bridge',
                'vessel': vessel,
                'status': 'operational'
            },
            {
                'name': 'Emergency Generator',
                'model': 'C32 ACERT',
                'serial_number': 'EG12348',
                'manufacturer': 'Caterpillar',
                'installation_date': today - timedelta(days=365*2),
                'location': 'Emergency Generator Room',
                'vessel': vessel,
                'status': 'operational'
            }
        ]

        created_equipment = {}
        for equip_data in equipment_list:
            try:
                equipment = Equipment.objects.create(**equip_data)
                created_equipment[equipment.name] = equipment
                self.stdout.write(f'Created equipment: {equipment.name}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating equipment {equip_data["name"]}: {str(e)}')
                )

        # Create maintenance tasks
        tasks = [
            {
                'equipment': created_equipment['Main Engine'],
                'task_name': 'Main Engine Oil Change',
                'description': 'Change main engine lubricating oil',
                'interval_unit': 'hours',
                'interval_value': 1000,
                'last_completed': today - timedelta(days=30),
                'next_due': today + timedelta(days=30),
                'estimated_duration': 240,  # minutes
                'required_parts': 'Engine oil filters, O-rings, Gaskets',
                'safety_instructions': 'Ensure engine is stopped and cooled down before starting maintenance'
            },
            {
                'equipment': created_equipment['Main Engine'],
                'task_name': 'Cylinder Head Inspection',
                'description': 'Inspect cylinder heads for wear and damage',
                'interval_unit': 'hours',
                'interval_value': 2000,
                'last_completed': today - timedelta(days=45),
                'next_due': today + timedelta(days=45),
                'estimated_duration': 480,
                'required_parts': 'Gaskets, O-rings',
                'safety_instructions': 'Follow proper lockout/tagout procedures'
            },
            {
                'equipment': created_equipment['Auxiliary Engine #1'],
                'task_name': 'Fuel Filter Replacement',
                'description': 'Replace fuel filters',
                'interval_unit': 'hours',
                'interval_value': 500,
                'last_completed': today - timedelta(days=15),
                'next_due': today + timedelta(days=15),
                'estimated_duration': 120,
                'required_parts': 'Fuel filters, O-rings',
                'safety_instructions': 'Ensure proper ventilation'
            },
            {
                'equipment': created_equipment['Radar System'],
                'task_name': 'Radar System Calibration',
                'description': 'Calibrate radar system',
                'interval_unit': 'months',
                'interval_value': 6,
                'last_completed': today - timedelta(days=90),
                'next_due': today + timedelta(days=90),
                'estimated_duration': 180,
                'required_parts': None,
                'safety_instructions': 'Follow radiation safety procedures'
            }
        ]

        for task_data in tasks:
            try:
                task = MaintenanceTask.objects.create(**task_data)
                self.stdout.write(f'Created maintenance task: {task.task_name}')

                # Create maintenance history
                history = MaintenanceHistory.objects.create(
                    task=task,
                    equipment=task.equipment,
                    completed_date=task.last_completed,
                    completed_by=system_user,
                    remarks='Routine maintenance completed',
                    running_hours=task.equipment.running_hours if hasattr(task.equipment, 'running_hours') else None,
                    parts_used='Standard replacement parts',
                    duration=task.estimated_duration
                )
                self.stdout.write(f'Created maintenance history for: {task.task_name}')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating task {task_data["task_name"]}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded PMS data')) 