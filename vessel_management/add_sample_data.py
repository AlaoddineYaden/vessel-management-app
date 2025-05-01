import os
import django
from datetime import date, timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crew.models import Crew, CrewCertificate, Vessel
from certificates.models import Certificate, CertificateType, CertificateRenewal

def add_sample_data():
    # Sample vessel data
    VESSEL_DATA = [
        {
            'name': 'Ocean Explorer',
            'imo_number': 'IMO9876543',
            'vessel_type': 'Container Ship',
        },
        {
            'name': 'Pacific Voyager',
            'imo_number': 'IMO8765432',
            'vessel_type': 'Bulk Carrier',
        },
        {
            'name': 'Atlantic Star',
            'imo_number': 'IMO7654321',
            'vessel_type': 'Tanker',
        }
    ]

    # Sample crew data
    CREW_DATA = [
        {
            'name': 'John Smith',
            'rank': 'CAPTAIN',
            'nationality': 'USA',
            'date_of_birth': date(1975, 6, 15),
            'passport_number': 'P1234567',
            'seaman_book_number': 'SB1234567',
            'phone_number': '+1-555-123-4567',
            'email': 'john.smith@example.com',
            'address': '123 Ocean Drive, Miami, FL',
            'emergency_contact_name': 'Jane Smith',
            'emergency_contact_phone': '+1-555-987-6543',
            'is_active': True,
        },
        {
            'name': 'Maria Garcia',
            'rank': 'CHIEF_ENGINEER',
            'nationality': 'Spain',
            'date_of_birth': date(1980, 3, 22),
            'passport_number': 'P2345678',
            'seaman_book_number': 'SB2345678',
            'phone_number': '+34-666-123-456',
            'email': 'maria.garcia@example.com',
            'address': 'Calle del Mar 45, Barcelona, Spain',
            'emergency_contact_name': 'Carlos Garcia',
            'emergency_contact_phone': '+34-666-987-654',
            'is_active': True,
        },
        {
            'name': 'Ahmed Hassan',
            'rank': 'CHIEF_MATE',
            'nationality': 'Egypt',
            'date_of_birth': date(1982, 11, 5),
            'passport_number': 'P3456789',
            'seaman_book_number': 'SB3456789',
            'phone_number': '+20-100-123-4567',
            'email': 'ahmed.hassan@example.com',
            'address': '15 Nile Street, Alexandria, Egypt',
            'emergency_contact_name': 'Fatima Hassan',
            'emergency_contact_phone': '+20-100-987-6543',
            'is_active': True,
        },
        {
            'name': 'Li Wei',
            'rank': 'SECOND_ENGINEER',
            'nationality': 'China',
            'date_of_birth': date(1985, 8, 30),
            'passport_number': 'P4567890',
            'seaman_book_number': 'SB4567890',
            'phone_number': '+86-138-1234-5678',
            'email': 'li.wei@example.com',
            'address': '88 Harbour Road, Shanghai, China',
            'emergency_contact_name': 'Wang Wei',
            'emergency_contact_phone': '+86-139-9876-5432',
            'is_active': True,
        },
        {
            'name': 'Ivan Petrov',
            'rank': 'THIRD_ENGINEER',
            'nationality': 'Russia',
            'date_of_birth': date(1988, 2, 14),
            'passport_number': 'P5678901',
            'seaman_book_number': 'SB5678901',
            'phone_number': '+7-916-123-4567',
            'email': 'ivan.petrov@example.com',
            'address': '45 Seafarer Street, Vladivostok, Russia',
            'emergency_contact_name': 'Olga Petrov',
            'emergency_contact_phone': '+7-916-987-6543',
            'is_active': True,
        }
    ]

    # Certificate types and their typical validity periods
    CREW_CERTIFICATE_TYPES = {
        'STCW': {
            'Basic Safety Training': 5,  # 5 years
            'Advanced Fire Fighting': 5,
            'Medical First Aid': 5,
            'Proficiency in Survival Craft': 5,
            'Security Awareness': 5,
        },
        'MEDICAL': {
            'Medical Fitness Certificate': 2,  # 2 years
            'Yellow Fever Vaccination': 10,  # 10 years
        },
        'COC': {
            'Chief Mate': 5,
            'Master Mariner': 5,
            'Chief Engineer': 5,
            'Second Engineer': 5,
        },
        'ENDORSEMENT': {
            'GMDSS': 5,
            'ECDIS': 5,
            'LNG': 5,
        }
    }

    # Vessel certificate types
    VESSEL_CERTIFICATE_TYPES = {
        'STATUTORY': {
            'International Tonnage Certificate': 5,
            'International Load Line Certificate': 5,
            'International Oil Pollution Prevention Certificate': 5,
            'International Sewage Pollution Prevention Certificate': 5,
            'International Air Pollution Prevention Certificate': 5,
            'International Ballast Water Management Certificate': 5,
            'International Anti-fouling System Certificate': 5,
            'International Ship Security Certificate': 5,
            'Safety Management Certificate': 5,
            'Document of Compliance': 5,
        },
        'CLASS': {
            'Classification Certificate': 5,
            'Cargo Ship Safety Construction Certificate': 5,
            'Cargo Ship Safety Equipment Certificate': 5,
            'Cargo Ship Safety Radio Certificate': 5,
            'Cargo Ship Safety Certificate': 5,
        },
        'OTHER': {
            'Port State Control Certificate': 1,
            'Insurance Certificate': 1,
            'Radio License': 1,
            'Deratting Certificate': 6,
            'Sanitation Certificate': 6,
        }
    }

    # Add vessels
    vessels_created = 0
    for vessel_data in VESSEL_DATA:
        vessel, created = Vessel.objects.get_or_create(
            imo_number=vessel_data['imo_number'],
            defaults=vessel_data
        )
        if created:
            vessels_created += 1
            print(f'Created vessel: {vessel.name} (IMO: {vessel.imo_number})')

    print(f'Successfully created {vessels_created} vessels')

    # Add crew members
    crew_created = 0
    for crew_data in CREW_DATA:
        crew, created = Crew.objects.get_or_create(
            email=crew_data['email'],
            defaults=crew_data
        )
        if created:
            crew_created += 1
            print(f'Created crew member: {crew.name} ({crew.rank})')

    print(f'Successfully created {crew_created} crew members')

    # Add crew certificates
    crew_certificates_created = 0
    for crew in Crew.objects.all():
        for cert_type, certs in CREW_CERTIFICATE_TYPES.items():
            for cert_name, validity_years in certs.items():
                # Randomize issue date between 1 and 3 years ago
                issue_date = timezone.now().date() - timedelta(days=365 * (1 + (crew_certificates_created % 3)))
                
                # Calculate expiry date based on validity period
                expiry_date = issue_date + timedelta(days=365 * validity_years)
                
                # Create certificate
                certificate, created = CrewCertificate.objects.get_or_create(
                    crew=crew,
                    certificate_type=cert_type,
                    certificate_name=cert_name,
                    defaults={
                        'certificate_number': f'{cert_type[:3]}-{crew.id}-{crew_certificates_created}',
                        'issue_date': issue_date,
                        'expiry_date': expiry_date,
                        'issuing_authority': 'Maritime Authority',
                        'document_file': None,
                    }
                )
                
                if created:
                    crew_certificates_created += 1
                    print(f'Created {cert_type} certificate "{cert_name}" for {crew.name}')

    print(f'Successfully created {crew_certificates_created} crew certificates')

    # Add vessel certificate types
    vessel_cert_types_created = 0
    for cert_type_name, certs in VESSEL_CERTIFICATE_TYPES.items():
        for cert_name, validity_years in certs.items():
            cert_type, created = CertificateType.objects.get_or_create(
                name=cert_name,
                defaults={
                    'description': f'{cert_type_name} certificate for vessels',
                    'is_statutory': cert_type_name == 'STATUTORY',
                    'renewal_period_days': validity_years * 365,
                }
            )
            if created:
                vessel_cert_types_created += 1
                print(f'Created certificate type: {cert_name}')

    print(f'Successfully created {vessel_cert_types_created} vessel certificate types')

    # Add vessel certificates with some expiring soon
    vessel_certificates_created = 0
    for vessel in Vessel.objects.all():
        for cert_type_name, certs in VESSEL_CERTIFICATE_TYPES.items():
            for cert_name, validity_years in certs.items():
                # For demonstration, make some certificates expire soon
                if vessel_certificates_created % 3 == 0:  # Every third certificate
                    # Make certificate expire in 15 days
                    issue_date = timezone.now().date() - timedelta(days=365 * validity_years - 15)
                    expiry_date = timezone.now().date() + timedelta(days=15)
                else:
                    # Normal issue date
                    issue_date = timezone.now().date() - timedelta(days=365 * (1 + (vessel_certificates_created % 3)))
                    expiry_date = issue_date + timedelta(days=365 * validity_years)
                
                # Get certificate type
                cert_type = CertificateType.objects.get(name=cert_name)
                
                # Create certificate
                certificate, created = Certificate.objects.get_or_create(
                    vessel=vessel,
                    certificate_type=cert_type,
                    defaults={
                        'certificate_name': cert_name,
                        'certificate_number': f'{cert_type_name[:3]}-{vessel.imo_number}-{vessel_certificates_created}',
                        'issue_date': issue_date,
                        'expiry_date': expiry_date,
                        'issuing_authority': 'Maritime Authority',
                        'status': 'active',
                        'document_file': None,
                    }
                )
                
                if created:
                    vessel_certificates_created += 1
                    print(f'Created {cert_type_name} certificate "{cert_name}" for {vessel.name}')

                    # Create renewal record for certificates expiring soon
                    if (expiry_date - timezone.now().date()).days <= 30:
                        renewal, _ = CertificateRenewal.objects.get_or_create(
                            certificate=certificate,
                            defaults={
                                'status': 'pending',
                                'due_date': expiry_date,
                                'renewal_cost': 1000.00,  # Sample cost
                                'notes': 'Certificate renewal required',
                            }
                        )
                        print(f'Created renewal record for {cert_name} of {vessel.name}')

    print(f'Successfully created {vessel_certificates_created} vessel certificates')

if __name__ == '__main__':
    add_sample_data() 