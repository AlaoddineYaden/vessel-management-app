from django.core.management.base import BaseCommand
from django.utils import timezone
from vessel_pms.models import Equipment
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seeds the database with sample maintenance data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding maintenance data...')
        
        # Create a test equipment
        equipment = Equipment.objects.create(
            name='Test Engine',
            model='Test Model',
            serial_number='TEST-001',
            manufacturer='Test Manufacturer',
            installation_date=timezone.now().date(),
            location='Engine Room',
            status='operational'
        )
        
        self.stdout.write(f'Created equipment: {equipment}')
        self.stdout.write(self.style.SUCCESS('Successfully seeded maintenance data')) 