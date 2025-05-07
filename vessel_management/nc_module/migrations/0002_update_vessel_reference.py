from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('nc_module', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- First, ensure vessels exist in core_vessel
            INSERT INTO core_vessel (id, name, imo_number, vessel_type, flag, build_year, length_overall, beam, draft, gross_tonnage, is_active, created_at, updated_at)
            SELECT DISTINCT nc.vessel_id, 
                   'Vessel ' || nc.vessel_id, 
                   'IMO' || nc.vessel_id,
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
            FROM nc_module_nonconformity nc
            WHERE NOT EXISTS (
                SELECT 1 FROM core_vessel cv WHERE cv.id = nc.vessel_id
            );
            
            -- Add the new vessel column
            ALTER TABLE nc_module_nonconformity
            ADD COLUMN vessel_id_new integer;
            
            -- Update the new column with the same values
            UPDATE nc_module_nonconformity
            SET vessel_id_new = vessel_id;
            
            -- Drop the old column
            ALTER TABLE nc_module_nonconformity
            DROP COLUMN vessel_id;
            
            -- Rename the new column
            ALTER TABLE nc_module_nonconformity
            RENAME COLUMN vessel_id_new TO vessel_id;
            
            -- Add foreign key constraint
            ALTER TABLE nc_module_nonconformity
            ADD CONSTRAINT nc_module_nonconformity_vessel_id_fk
            FOREIGN KEY (vessel_id) REFERENCES core_vessel(id)
            ON DELETE CASCADE;
            """,
            reverse_sql="""
            -- Remove foreign key constraint
            ALTER TABLE nc_module_nonconformity
            DROP CONSTRAINT nc_module_nonconformity_vessel_id_fk;
            
            -- Add a temporary column
            ALTER TABLE nc_module_nonconformity
            ADD COLUMN vessel_id_old integer;
            
            -- Copy data
            UPDATE nc_module_nonconformity
            SET vessel_id_old = vessel_id;
            
            -- Drop the foreign key column
            ALTER TABLE nc_module_nonconformity
            DROP COLUMN vessel_id;
            
            -- Rename the old column back
            ALTER TABLE nc_module_nonconformity
            RENAME COLUMN vessel_id_old TO vessel_id;
            """
        ),
    ] 