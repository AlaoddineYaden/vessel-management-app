from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('vessel_pms', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # First, ensure at least one vessel exists in core_vessel
            sql="""
            INSERT INTO core_vessel (id, name, imo_number, vessel_type, flag, build_year, length_overall, beam, draft, gross_tonnage, is_active, created_at, updated_at)
            SELECT 1, 
                   'Default Vessel', 
                   'IMO1234567',
                   'Unknown',
                   'Unknown',
                   2000,
                   100,
                   20,
                   10,
                   1000,
                   true,
                   NOW(),
                   NOW()
            WHERE NOT EXISTS (
                SELECT 1 FROM core_vessel LIMIT 1
            );
            """,
            reverse_sql="""
            -- No need to remove the vessel as it might be used by other apps
            """
        ),
        migrations.AddField(
            model_name='equipment',
            name='vessel',
            field=models.ForeignKey(
                to='core.vessel',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='equipment',
                null=True  # Temporarily allow null
            ),
        ),
        migrations.RunSQL(
            # Set default vessel for existing equipment
            sql="""
            UPDATE vessel_pms_equipment
            SET vessel_id = (SELECT id FROM core_vessel LIMIT 1)
            WHERE vessel_id IS NULL;
            """,
            reverse_sql="""
            UPDATE vessel_pms_equipment
            SET vessel_id = NULL;
            """
        ),
        migrations.AlterField(
            model_name='equipment',
            name='vessel',
            field=models.ForeignKey(
                to='core.vessel',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='equipment'
            ),
        ),
    ] 