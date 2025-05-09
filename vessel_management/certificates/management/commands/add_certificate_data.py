from django.core.management.base import BaseCommand
from django.utils import timezone
from certificates.models import CertificateType, Certificate, CertificateRenewal
from core.models import Vessel
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seeds the database with sample certificate data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding certificate data...')

        # Get the vessel
        vessel = Vessel.objects.first()
        if not vessel:
            self.stdout.write(self.style.ERROR('No vessels found in the database. Please create a vessel first.'))
            return

        # Remove existing data
        self.stdout.write('Removing existing certificate data...')
        CertificateRenewal.objects.all().delete()
        self.stdout.write('Deleted all certificate renewals')
        
        Certificate.objects.all().delete()
        self.stdout.write('Deleted all certificates')
        
        CertificateType.objects.all().delete()
        self.stdout.write('Deleted all certificate types')

        # Create certificate types
        certificate_types = [
            {
                'name': 'Safety Management Certificate (SMC)',
                'description': 'Certifies that the vessel\'s safety management system complies with ISM Code requirements',
                'is_statutory': True,
                'renewal_period_days': 1825  # 5 years
            },
            {
                'name': 'International Load Line Certificate',
                'description': 'Certifies that the vessel has been surveyed and marked with load lines',
                'is_statutory': True,
                'renewal_period_days': 1825  # 5 years
            },
            {
                'name': 'International Oil Pollution Prevention Certificate (IOPPC)',
                'description': 'Certifies compliance with MARPOL Annex I requirements',
                'is_statutory': True,
                'renewal_period_days': 1825  # 5 years
            },
            {
                'name': 'Cargo Ship Safety Construction Certificate',
                'description': 'Certifies that the vessel\'s structure, machinery, and equipment meet SOLAS requirements',
                'is_statutory': True,
                'renewal_period_days': 1825  # 5 years
            },
            {
                'name': 'Classification Certificate',
                'description': 'Certifies that the vessel meets class society requirements',
                'is_statutory': False,
                'renewal_period_days': 1825  # 5 years
            },
            {
                'name': 'Document of Compliance (DOC)',
                'description': 'Company compliance with ISM Code requirements',
                'is_statutory': True,
                'renewal_period_days': 1825  # 5 years
            },
            {
                'name': 'International Air Pollution Prevention Certificate (IAPP)',
                'description': 'Certifies compliance with MARPOL Annex VI requirements',
                'is_statutory': True,
                'renewal_period_days': 1825  # 5 years
            },
            {
                'name': 'International Sewage Pollution Prevention Certificate (ISPP)',
                'description': 'Certifies compliance with MARPOL Annex IV requirements',
                'is_statutory': True,
                'renewal_period_days': 1825  # 5 years
            },
            {
                'name': 'International Ballast Water Management Certificate',
                'description': 'Certifies compliance with Ballast Water Management Convention',
                'is_statutory': True,
                'renewal_period_days': 1825  # 5 years
            },
            {
                'name': 'Cargo Ship Safety Equipment Certificate',
                'description': 'Certifies that the vessel\'s safety equipment meets SOLAS requirements',
                'is_statutory': True,
                'renewal_period_days': 1825  # 5 years
            }
        ]

        for type_data in certificate_types:
            cert_type = CertificateType.objects.create(**type_data)
            self.stdout.write(f'Created certificate type: {cert_type.name}')

        # Create certificates
        today = timezone.now().date()
        certificates = [
            {
                'certificate_name': 'Safety Management Certificate',
                'certificate_type': CertificateType.objects.get(name='Safety Management Certificate (SMC)'),
                'certificate_number': 'SMC-2023-001',
                'issue_date': today - timedelta(days=365),
                'expiry_date': today + timedelta(days=1095),  # Valid for 3 more years
                'issuing_authority': 'DNV GL',
                'vessel': vessel,
                'notes': 'Initial certification after successful ISM audit'
            },
            {
                'certificate_name': 'Load Line Certificate',
                'certificate_type': CertificateType.objects.get(name='International Load Line Certificate'),
                'certificate_number': 'LLC-2023-001',
                'issue_date': today - timedelta(days=180),
                'expiry_date': today + timedelta(days=1645),  # Valid for 4.5 years
                'issuing_authority': 'Bureau Veritas',
                'vessel': vessel,
                'notes': 'Annual survey completed'
            },
            {
                'certificate_name': 'IOPP Certificate',
                'certificate_type': CertificateType.objects.get(name='International Oil Pollution Prevention Certificate (IOPPC)'),
                'certificate_number': 'IOPP-2023-001',
                'issue_date': today - timedelta(days=25),
                'expiry_date': today + timedelta(days=20),  # About to expire
                'issuing_authority': 'Lloyd\'s Register',
                'vessel': vessel,
                'notes': 'Renewal survey due'
            },
            {
                'certificate_name': 'Safety Construction Certificate',
                'certificate_type': CertificateType.objects.get(name='Cargo Ship Safety Construction Certificate'),
                'certificate_number': 'SCC-2023-001',
                'issue_date': today - timedelta(days=730),  # 2 years ago
                'expiry_date': today - timedelta(days=1),  # Just expired
                'issuing_authority': 'American Bureau of Shipping',
                'vessel': vessel,
                'notes': 'Renewal required'
            },
            {
                'certificate_name': 'Classification Certificate',
                'certificate_type': CertificateType.objects.get(name='Classification Certificate'),
                'certificate_number': 'CLASS-2023-001',
                'issue_date': today - timedelta(days=90),
                'expiry_date': today + timedelta(days=1735),  # Valid for 4.75 years
                'issuing_authority': 'DNV GL',
                'vessel': vessel,
                'notes': 'Annual survey completed with no conditions'
            },
            {
                'certificate_name': 'Document of Compliance',
                'certificate_type': CertificateType.objects.get(name='Document of Compliance (DOC)'),
                'certificate_number': 'DOC-2023-001',
                'issue_date': today - timedelta(days=180),
                'expiry_date': today + timedelta(days=1645),  # Valid for 4.5 years
                'issuing_authority': 'Lloyd\'s Register',
                'vessel': vessel,
                'notes': 'Company audit completed successfully'
            },
            {
                'certificate_name': 'IAPP Certificate',
                'certificate_type': CertificateType.objects.get(name='International Air Pollution Prevention Certificate (IAPP)'),
                'certificate_number': 'IAPP-2023-001',
                'issue_date': today - timedelta(days=15),
                'expiry_date': today + timedelta(days=30),  # Expiring soon
                'issuing_authority': 'Bureau Veritas',
                'vessel': vessel,
                'notes': 'Renewal survey scheduled'
            },
            {
                'certificate_name': 'ISPP Certificate',
                'certificate_type': CertificateType.objects.get(name='International Sewage Pollution Prevention Certificate (ISPP)'),
                'certificate_number': 'ISPP-2023-001',
                'issue_date': today - timedelta(days=365),
                'expiry_date': today + timedelta(days=1460),  # Valid for 4 years
                'issuing_authority': 'DNV GL',
                'vessel': vessel,
                'notes': 'Annual survey completed'
            },
            {
                'certificate_name': 'Ballast Water Management Certificate',
                'certificate_type': CertificateType.objects.get(name='International Ballast Water Management Certificate'),
                'certificate_number': 'BWMC-2023-001',
                'issue_date': today - timedelta(days=730),  # 2 years ago
                'expiry_date': today - timedelta(days=30),  # Expired
                'issuing_authority': 'American Bureau of Shipping',
                'vessel': vessel,
                'notes': 'Renewal required - system upgrade needed'
            },
            {
                'certificate_name': 'Safety Equipment Certificate',
                'certificate_type': CertificateType.objects.get(name='Cargo Ship Safety Equipment Certificate'),
                'certificate_number': 'SEC-2023-001',
                'issue_date': today - timedelta(days=180),
                'expiry_date': today + timedelta(days=1645),  # Valid for 4.5 years
                'issuing_authority': 'Lloyd\'s Register',
                'vessel': vessel,
                'notes': 'Annual survey completed with minor observations'
            }
        ]

        for cert_data in certificates:
            try:
                certificate = Certificate.objects.create(**cert_data)
                self.stdout.write(f'Created certificate: {certificate.certificate_name}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating certificate {cert_data["certificate_name"]}: {str(e)}')
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded certificate data')) 