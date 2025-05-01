from django.core.management.base import BaseCommand
from django.utils import timezone
from certificates.models import Certificate, CertificateRenewal

class Command(BaseCommand):
    help = 'Creates renewal records for all expired or expiring certificates that do not have renewal records'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Get all expired or expiring certificates
        certificates = Certificate.objects.filter(
            expiry_date__lte=today + timezone.timedelta(days=30)  # Expired or expiring within 30 days
        ).exclude(
            status__in=['revoked', 'suspended']  # Exclude certificates that shouldn't be renewed
        )
        
        renewals_created = 0
        for cert in certificates:
            days_to_expiry = (cert.expiry_date - today).days
            
            # Create renewal if it doesn't exist
            renewal, created = CertificateRenewal.objects.get_or_create(
                certificate=cert,
                defaults={
                    'status': 'pending',
                    'due_date': cert.expiry_date,
                    'renewal_cost': None,
                    'notes': f'Certificate {"expired" if days_to_expiry <= 0 else "expiring soon"} - renewal required',
                }
            )
            
            if created:
                renewals_created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created renewal record for {cert.certificate_name} ({cert.certificate_number})'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {renewals_created} renewal records'
            )
        ) 