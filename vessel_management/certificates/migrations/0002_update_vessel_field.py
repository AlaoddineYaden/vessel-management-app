from django.db import migrations, models
import django.db.models.deletion

def remove_invalid_vessel_references(apps, schema_editor):
    Certificate = apps.get_model('certificates', 'Certificate')
    Vessel = apps.get_model('core', 'Vessel')
    
    # Get all vessel IDs that exist in core.Vessel
    valid_vessel_ids = set(Vessel.objects.values_list('id', flat=True))
    
    # Update certificates with invalid vessel references to have null vessel
    Certificate.objects.exclude(vessel_id__in=valid_vessel_ids).update(vessel_id=None)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('certificates', '0001_initial'),
    ]

    operations = [
        # First, run the function to clean up invalid references
        migrations.RunPython(remove_invalid_vessel_references),
        
        # Then alter the field
        migrations.AlterField(
            model_name='certificate',
            name='vessel',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='certificates',
                to='core.vessel'
            ),
        ),
    ] 