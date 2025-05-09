import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Vessel

def add_sample_vessel():
    vessel_data = {
        'name': 'Ocean Explorer',
        'imo_number': 'IMO1234567',
        'mmsi_number': '123456789',
        'call_sign': 'ABCD',
        'vessel_type': 'CONTAINER',
        'flag': 'Panama',
        'build_year': 2015,
        'length_overall': 300.00,
        'beam': 40.00,
        'draft': 14.00,
        'gross_tonnage': 50000.00,
        'net_tonnage': 25000.00,
        'is_active': True,
        'notes': 'Sample vessel for testing'
    }
    
    vessel, created = Vessel.objects.get_or_create(
        imo_number=vessel_data['imo_number'],
        defaults=vessel_data
    )
    
    if created:
        print(f"Created vessel: {vessel.name}")
    else:
        print(f"Vessel already exists: {vessel.name}")
    
    return vessel

if __name__ == '__main__':
    add_sample_vessel() 