from django.db import migrations

def migrate_vessel_data(apps, schema_editor):
    Certificate = apps.get_model('certificates', 'Certificate')
    Vessel = apps.get_model('core', 'Vessel')
    
    # For each certificate with a vessel_id, find the corresponding vessel
    for certificate in Certificate.objects.all():
        if hasattr(certificate, 'vessel_id') and certificate.vessel_id:
            try:
                vessel = Vessel.objects.get(id=certificate.vessel_id)
                certificate.vessel = vessel
                certificate.save()
            except Vessel.DoesNotExist:
                # If vessel doesn't exist, set to None
                certificate.vessel = None
                certificate.save()

class Migration(migrations.Migration):

    dependencies = [
        ('certificates', '0002_update_vessel_field'),
    ]

    operations = [
        migrations.RunPython(migrate_vessel_data),
    ] 