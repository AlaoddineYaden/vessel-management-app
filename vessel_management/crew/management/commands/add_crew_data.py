from django.core.management.base import BaseCommand
from django.utils import timezone
from crew.models import Crew, CrewCertificate
from core.models import Vessel
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seeds the database with sample crew data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding crew data...')

        # Get the vessel
        vessel = Vessel.objects.first()
        if not vessel:
            self.stdout.write(self.style.ERROR('No vessels found in the database. Please create a vessel first.'))
            return

        # Create crew members
        crew_members = [
            {
                'name': 'John Smith',
                'rank': 'CAPTAIN',
                'nationality': 'British',
                'date_of_birth': '1975-06-15',
                'passport_number': 'GB123456',
                'seaman_book_number': 'SB789012',
                'phone_number': '+44123456789',
                'email': 'john.smith@example.com',
                'address': '123 Maritime Street, London, UK',
                'emergency_contact_name': 'Sarah Smith',
                'emergency_contact_phone': '+44123456790',
                'medical_information': 'No known medical conditions',
                'notes': 'Experienced captain with 15 years of service'
            },
            {
                'name': 'Maria Garcia',
                'rank': 'CHIEF_ENGINEER',
                'nationality': 'Spanish',
                'date_of_birth': '1980-03-22',
                'passport_number': 'ES789012',
                'seaman_book_number': 'SB345678',
                'phone_number': '+34678901234',
                'email': 'maria.garcia@example.com',
                'address': '456 Engineer Road, Barcelona, Spain',
                'emergency_contact_name': 'Carlos Garcia',
                'emergency_contact_phone': '+34678901235',
                'medical_information': 'Allergic to penicillin',
                'notes': 'Specialized in marine diesel engines'
            },
            {
                'name': 'James Wilson',
                'rank': 'CHIEF_OFFICER',
                'nationality': 'American',
                'date_of_birth': '1982-11-30',
                'passport_number': 'US456789',
                'seaman_book_number': 'SB901234',
                'phone_number': '+12125551234',
                'email': 'james.wilson@example.com',
                'address': '789 Navigation Ave, Miami, USA',
                'emergency_contact_name': 'Emily Wilson',
                'emergency_contact_phone': '+12125551235',
                'medical_information': 'None',
                'notes': 'Expert in navigation and cargo operations'
            }
        ]

        for crew_data in crew_members:
            try:
                crew = Crew.objects.create(**crew_data)
                self.stdout.write(f'Created crew member: {crew.name} ({crew.rank})')

                # Add certificates for each crew member
                today = timezone.now().date()
                certificates = [
                    {
                        'certificate_type': 'COC',
                        'certificate_name': 'Master Mariner Certificate',
                        'certificate_number': f'COC-{crew.passport_number}',
                        'issue_date': today - timedelta(days=365),
                        'expiry_date': today + timedelta(days=1095),
                        'issuing_authority': 'Maritime and Coastguard Agency',
                        'notes': 'Unlimited tonnage'
                    } if crew.rank == 'CAPTAIN' else {
                        'certificate_type': 'COC',
                        'certificate_name': 'Chief Engineer Certificate',
                        'certificate_number': f'COC-{crew.passport_number}',
                        'issue_date': today - timedelta(days=365),
                        'expiry_date': today + timedelta(days=1095),
                        'issuing_authority': 'Spanish Maritime Authority',
                        'notes': 'Unlimited horsepower'
                    } if crew.rank == 'CHIEF_ENGINEER' else {
                        'certificate_type': 'COC',
                        'certificate_name': 'Chief Officer Certificate',
                        'certificate_number': f'COC-{crew.passport_number}',
                        'issue_date': today - timedelta(days=365),
                        'expiry_date': today + timedelta(days=1095),
                        'issuing_authority': 'US Coast Guard',
                        'notes': 'Unlimited tonnage'
                    },
                    {
                        'certificate_type': 'MEDICAL',
                        'certificate_name': 'Seafarer Medical Certificate',
                        'certificate_number': f'MED-{crew.passport_number}',
                        'issue_date': today - timedelta(days=180),
                        'expiry_date': today + timedelta(days=180),
                        'issuing_authority': 'Maritime Medical Center',
                        'notes': 'Valid for 1 year'
                    },
                    {
                        'certificate_type': 'STCW',
                        'certificate_name': 'STCW Basic Safety Training',
                        'certificate_number': f'STCW-{crew.passport_number}',
                        'issue_date': today - timedelta(days=730),
                        'expiry_date': today + timedelta(days=730),
                        'issuing_authority': 'Maritime Training Center',
                        'notes': 'Includes firefighting and survival techniques'
                    }
                ]

                for cert_data in certificates:
                    cert = CrewCertificate.objects.create(crew=crew, **cert_data)
                    self.stdout.write(f'Created certificate: {cert.certificate_name} for {crew.name}')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating crew member {crew_data["name"]}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded crew data')) 