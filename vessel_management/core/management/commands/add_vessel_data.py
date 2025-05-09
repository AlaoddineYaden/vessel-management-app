from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Vessel
from datetime import timedelta

class Command(BaseCommand):
    help = 'Adds more vessel data to the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Adding vessel data...')

        # Sample vessel data
        vessels = [
            {
                'name': 'Tug Master I',
                'imo_number': 'IMO9876543',
                'mmsi_number': '123456789',
                'call_sign': 'ABCD',
                'flag': 'Panama',
                'vessel_type': 'TUG',
                'gross_tonnage': 500.00,
                'net_tonnage': 250.00,
                'length_overall': 35.5,
                'beam': 12.0,
                'draft': 4.5,
                'build_year': 2015,
                'is_active': True,
                'notes': 'Sample tug vessel for testing'
            },
            {
                'name': 'Tug Master II',
                'imo_number': 'IMO9876544',
                'mmsi_number': '123456790',
                'call_sign': 'ABCE',
                'flag': 'Panama',
                'vessel_type': 'TUG',
                'gross_tonnage': 550.00,
                'net_tonnage': 275.00,
                'length_overall': 36.0,
                'beam': 12.5,
                'draft': 4.8,
                'build_year': 2016,
                'is_active': True,
                'notes': 'Sample tug vessel for testing'
            }
        ]

        for vessel_data in vessels:
            try:
                vessel = Vessel.objects.create(**vessel_data)
                self.stdout.write(f'Created vessel: {vessel.name}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating vessel {vessel_data["name"]}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS('Successfully added vessel data')) 