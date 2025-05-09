from django.core.management.base import BaseCommand
import pandas as pd
import os
from vessel_pms.models import Equipment, MaintenanceTask
from django.utils import timezone
from datetime import datetime
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Imports data from the remorqueur files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip existing records instead of updating them',
        )

    def validate_equipment_data(self, row):
        """Validate equipment data before creation"""
        if pd.isna(row.iloc[0]) or pd.isna(row.iloc[1]):
            raise ValueError("Equipment name and code are required")
        return {
            'name': str(row.iloc[0]).strip(),
            'serial_number': str(row.iloc[1]).strip(),
            'model': str(row.iloc[2]).strip() if len(row) > 2 and not pd.isna(row.iloc[2]) else '',
            'manufacturer': str(row.iloc[3]).strip() if len(row) > 3 and not pd.isna(row.iloc[3]) else '',
            'installation_date': timezone.now().date(),
            'location': str(row.iloc[4]).strip() if len(row) > 4 and not pd.isna(row.iloc[4]) else '',
            'status': 'operational'
        }

    def validate_task_data(self, row):
        """Validate maintenance task data before creation"""
        if pd.isna(row.iloc[0]):
            raise ValueError("Task name is required")
        return {
            'name': str(row.iloc[0]).strip(),
            'description': str(row.iloc[1]).strip() if len(row) > 1 and not pd.isna(row.iloc[1]) else '',
            'interval_value': int(row.iloc[2]) if len(row) > 2 and not pd.isna(row.iloc[2]) else 30,
            'interval_unit': 'days',
            'status': 'pending',
            'priority': str(row.iloc[3]).lower() if len(row) > 3 and not pd.isna(row.iloc[3]) else 'medium',
            'estimated_hours': float(row.iloc[4]) if len(row) > 4 and not pd.isna(row.iloc[4]) else 1.0,
            'instructions': str(row.iloc[5]).strip() if len(row) > 5 and not pd.isna(row.iloc[5]) else ''
        }

    def import_excel_data(self, file_path, model_class, validator_func, description):
        """Generic function to import data from Excel files"""
        try:
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
                return

            df = pd.read_excel(file_path)
            self.stdout.write(f'Found {len(df)} {description} records')
            
            created_count = 0
            updated_count = 0
            error_count = 0
            
            for idx, row in df.iterrows():
                try:
                    data = validator_func(row)
                    obj, created = model_class.objects.update_or_create(
                        name=data.pop('name'),
                        defaults=data
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                    self.stdout.write(f'{"Created" if created else "Updated"} {description}: {obj.name}')
                except (ValueError, IntegrityError) as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'Error processing row {idx + 2}: {str(e)}'))
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f'Unexpected error in row {idx + 2}: {str(e)}'))
            
            self.stdout.write(self.style.SUCCESS(
                f'{description} import complete: {created_count} created, {updated_count} updated, {error_count} errors'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading {description} file: {str(e)}'))

    def handle(self, *args, **options):
        self.stdout.write('Starting remorqueur data import...')
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), 'fichiers remorqueur')

        # Import equipment data
        equipment_file = os.path.join(base_dir, 'equipements_bab_almarasa_6chiffres.xlsx')
        self.import_excel_data(equipment_file, Equipment, self.validate_equipment_data, 'equipment')

        # Import maintenance tasks from component jobs
        tasks_file = os.path.join(base_dir, 'component_jobs.xlsx')
        self.import_excel_data(tasks_file, MaintenanceTask, self.validate_task_data, 'maintenance task')

        # Import maintenance plan tasks
        plan_file = os.path.join(base_dir, 'Plan 2024 forma A4 de maintenance préventive BAB ALMARSA (2).xlsx')
        self.import_excel_data(plan_file, MaintenanceTask, self.validate_task_data, 'maintenance plan task')

        self.stdout.write(self.style.SUCCESS('Successfully completed remorqueur data import')) 