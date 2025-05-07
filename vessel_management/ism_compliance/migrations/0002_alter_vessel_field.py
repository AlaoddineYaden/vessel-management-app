from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('ism_compliance', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # Drop the old index and constraint
            sql="""
            DROP INDEX IF EXISTS ism_complia_vessel__71e5ca_idx;
            ALTER TABLE ism_compliance_complianceitem DROP CONSTRAINT IF EXISTS ism_compliance_complianceitem_ism_requirement_id_vessel_id_0a7a3e7c_uniq;
            """,
            reverse_sql="""
            CREATE INDEX ism_complia_vessel__71e5ca_idx ON ism_compliance_complianceitem(vessel_id);
            ALTER TABLE ism_compliance_complianceitem ADD CONSTRAINT ism_compliance_complianceitem_ism_requirement_id_vessel_id_0a7a3e7c_uniq UNIQUE (ism_requirement_id, vessel_id);
            """
        ),
        migrations.RunSQL(
            # Add new column and migrate data
            sql="""
            ALTER TABLE ism_compliance_complianceitem
            ADD COLUMN vessel_id_new integer;
            
            -- Update the new column with corresponding vessel IDs
            UPDATE ism_compliance_complianceitem ci
            SET vessel_id_new = (
                SELECT id 
                FROM core_vessel cv 
                WHERE cv.imo_number::text = ci.vessel_id::text
                LIMIT 1
            );
            
            -- Drop the old column and rename the new one
            ALTER TABLE ism_compliance_complianceitem
            DROP COLUMN vessel_id;
            
            ALTER TABLE ism_compliance_complianceitem
            RENAME COLUMN vessel_id_new TO vessel_id;
            
            -- Add NOT NULL constraint and foreign key
            ALTER TABLE ism_compliance_complianceitem
            ALTER COLUMN vessel_id SET NOT NULL;
            
            ALTER TABLE ism_compliance_complianceitem
            ADD CONSTRAINT ism_compliance_complianceitem_vessel_id_fk
            FOREIGN KEY (vessel_id) REFERENCES core_vessel(id)
            ON DELETE CASCADE;
            """,
            reverse_sql="""
            ALTER TABLE ism_compliance_complianceitem
            DROP CONSTRAINT ism_compliance_complianceitem_vessel_id_fk;
            
            ALTER TABLE ism_compliance_complianceitem
            ADD COLUMN vessel_id_old varchar(20);
            
            UPDATE ism_compliance_complianceitem ci
            SET vessel_id_old = (
                SELECT imo_number 
                FROM core_vessel cv 
                WHERE cv.id = ci.vessel_id
                LIMIT 1
            );
            
            ALTER TABLE ism_compliance_complianceitem
            DROP COLUMN vessel_id;
            
            ALTER TABLE ism_compliance_complianceitem
            RENAME COLUMN vessel_id_old TO vessel_id;
            """
        ),
        migrations.AddConstraint(
            model_name='complianceitem',
            constraint=models.UniqueConstraint(
                fields=('ism_requirement', 'vessel'),
                name='unique_requirement_vessel'
            ),
        ),
    ] 