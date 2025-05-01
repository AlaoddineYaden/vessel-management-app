from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from vessel_pms.models import Equipment
from core.models import Vessel
from safety_procedures.models import ProcedureCategory, Procedure
from ism_compliance.models import ISMRequirement
from crew.models import Crew
from nc_module.models import NonConformity
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create admin user if not exists
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write('Created admin user')

        # Create sample vessels
        vessels = [
            {
                'name': 'Ocean Voyager',
                'imo_number': '9876543',
                'mmsi_number': '123456789',
                'call_sign': 'ABCD',
                'vessel_type': 'Container Ship',
                'flag': 'Panama',
                'build_year': 2015,
                'length_overall': 366.0,
                'beam': 48.2,
                'draft': 15.0,
                'gross_tonnage': 150000,
                'net_tonnage': 120000,
            },
            {
                'name': 'Pacific Explorer',
                'imo_number': '9876544',
                'mmsi_number': '123456790',
                'call_sign': 'EFGH',
                'vessel_type': 'Bulk Carrier',
                'flag': 'Liberia',
                'build_year': 2018,
                'length_overall': 292.0,
                'beam': 45.0,
                'draft': 14.5,
                'gross_tonnage': 95000,
                'net_tonnage': 75000,
            },
            {
                'name': 'Atlantic Pioneer',
                'imo_number': '9876545',
                'mmsi_number': '123456791',
                'call_sign': 'IJKL',
                'vessel_type': 'Tanker',
                'flag': 'Marshall Islands',
                'build_year': 2020,
                'length_overall': 333.0,
                'beam': 60.0,
                'draft': 20.0,
                'gross_tonnage': 180000,
                'net_tonnage': 150000,
            }
        ]

        vessel_objects = []
        for vessel_data in vessels:
            vessel = Vessel.objects.create(
                created_by=admin,
                updated_by=admin,
                **vessel_data
            )
            vessel_objects.append(vessel)
            self.stdout.write(f'Created vessel: {vessel.name}')

        # Create sample equipment
        equipment_types = ['Main Engine', 'Auxiliary Engine', 'Boiler', 'Pump', 'Generator']
        manufacturers = ['MAN', 'Wärtsilä', 'Caterpillar', 'Siemens', 'ABB']
        
        for vessel in vessel_objects:
            for i in range(5):
                Equipment.objects.create(
                    name=f'{random.choice(equipment_types)} {i+1}',
                    equipment_type=random.choice(equipment_types),
                    serial_number=f'SN-{vessel.imo_number}-{i+1}',
                    manufacturer=random.choice(manufacturers),
                    model=f'Model-{random.randint(1000, 9999)}',
                    installation_date=timezone.now() - timedelta(days=random.randint(100, 1000)),
                    location=f'Deck {random.randint(1, 5)}',
                    status=random.choice(['operational', 'maintenance', 'faulty']),
                )
            self.stdout.write(f'Created equipment for vessel: {vessel.name}')

        # Create sample procedure categories
        categories = [
            {'name': 'Safety Management', 'code': 'SM'},
            {'name': 'Emergency Procedures', 'code': 'EP'},
            {'name': 'Navigation', 'code': 'NAV'},
            {'name': 'Maintenance', 'code': 'MNT'},
            {'name': 'Environmental Protection', 'code': 'ENV'}
        ]

        category_objects = []
        for category_data in categories:
            category = ProcedureCategory.objects.create(
                name=category_data['name'],
                code=category_data['code'],
                description=f'Sample description for {category_data["name"]}'
            )
            category_objects.append(category)
            self.stdout.write(f'Created category: {category.name}')

        # Create sample procedures
        for category in category_objects:
            for i in range(3):
                Procedure.objects.create(
                    title=f'Sample Procedure {i+1} for {category.name}',
                    document_type=random.choice(['PROCEDURE', 'CHECKLIST', 'MANUAL']),
                    category=category,
                    content=f'This is a sample procedure content for {category.name}',
                    version='1.0',
                    created_by=admin,
                    review_interval_months=12,
                    is_active=True,
                    tags='sample,test'
                )
            self.stdout.write(f'Created procedures for category: {category.name}')

        # Create sample ISM requirements
        ism_requirements = [
            {'code': 'ISM-1', 'title': 'Safety and Environmental Protection Policy', 'category': 'General'},
            {'code': 'ISM-2', 'title': 'Company Responsibilities and Authority', 'category': 'Management'},
            {'code': 'ISM-3', 'title': 'Designated Person(s)', 'category': 'Management'},
            {'code': 'ISM-4', 'title': 'Master\'s Responsibility and Authority', 'category': 'Operations'},
            {'code': 'ISM-5', 'title': 'Resources and Personnel', 'category': 'Management'}
        ]

        for req in ism_requirements:
            ISMRequirement.objects.create(
                code=req['code'],
                title=req['title'],
                description=f'Sample description for {req["title"]}',
                category=req['category']
            )
            self.stdout.write(f'Created ISM requirement: {req["code"]}')

        # Create sample crew members
        ranks = ['Captain', 'Chief Engineer', 'First Officer', 'Second Officer', 'Chief Cook']
        nationalities = ['Philippines', 'India', 'Ukraine', 'Greece', 'Croatia']
        
        for i in range(15):
            Crew.objects.create(
                first_name=f'Crew{i+1}',
                last_name=f'Member{i+1}',
                date_of_birth=timezone.now() - timedelta(days=random.randint(7000, 12000)),
                nationality=random.choice(nationalities),
                rank=random.choice(ranks),
                status=random.choice(['active', 'on_leave', 'in_transit'])
            )
            self.stdout.write(f'Created crew member: Crew{i+1} Member{i+1}')

        # Create sample non-conformities
        for vessel in vessel_objects:
            for i in range(3):
                NonConformity.objects.create(
                    description=f'Sample non-conformity {i+1} for {vessel.name}',
                    detection_date=timezone.now().date() - timedelta(days=random.randint(1, 30)),
                    source_type=random.choice(['INSPECTION', 'AUDIT', 'COMPLAINT']),
                    severity=random.choice(['LOW', 'MEDIUM', 'HIGH']),
                    vessel_id=vessel.id,
                    status=random.choice(['OPEN', 'IN_PROGRESS', 'CLOSED']),
                    root_cause=f'Sample root cause for non-conformity {i+1}',
                    created_by=admin,
                    updated_by=admin
                )
            self.stdout.write(f'Created non-conformities for vessel: {vessel.name}')

        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data')) 