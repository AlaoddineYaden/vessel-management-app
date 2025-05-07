from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from crew.models import Crew, CrewCertificate, CertificateNotification
from vessel_pms.models import Equipment, MaintenanceTask, MaintenanceHistory

class Command(BaseCommand):
    help = 'Sets up crew groups with specific permissions based on rank'

    def handle(self, *args, **kwargs):
        # Define group permissions mapping
        group_permissions = {
            'Fleet Manager': {
                'crew': ['view', 'add', 'change', 'delete'],
                'crewcertificate': ['view', 'add', 'change', 'delete'],
                'certificatenotification': ['view', 'add', 'change', 'delete'],
                'equipment': ['view', 'add', 'change', 'delete'],
                'maintenancetask': ['view', 'add', 'change', 'delete'],
                'maintenancehistory': ['view', 'add', 'change', 'delete']
            },
            'Chief Engineer': {
                'equipment': ['view', 'change'],
                'maintenancetask': ['view', 'add', 'change'],
                'maintenancehistory': ['view', 'add', 'change'],
                'crewcertificate': ['view'],
                'certificatenotification': ['view']
            },
            'Second Engineer': {
                'equipment': ['view'],
                'maintenancetask': ['view', 'change'],
                'maintenancehistory': ['view', 'add'],
                'crewcertificate': ['view'],
                'certificatenotification': ['view']
            },
            'Chief Officer': {
                'equipment': ['view', 'change'],
                'maintenancetask': ['view', 'add', 'change'],
                'maintenancehistory': ['view', 'add', 'change'],
                'crewcertificate': ['view'],
                'certificatenotification': ['view']
            },
            'Second Officer': {
                'equipment': ['view'],
                'maintenancetask': ['view', 'change'],
                'maintenancehistory': ['view', 'add'],
                'crewcertificate': ['view'],
                'certificatenotification': ['view']
            },
            'Third Officer': {
                'equipment': ['view'],
                'maintenancetask': ['view'],
                'maintenancehistory': ['view', 'add'],
                'crewcertificate': ['view'],
                'certificatenotification': ['view']
            },
            'Captain': {
                'crew': ['view', 'add', 'change'],
                'crewcertificate': ['view', 'add', 'change'],
                'certificatenotification': ['view', 'add', 'change'],
                'equipment': ['view', 'change'],
                'maintenancetask': ['view', 'add', 'change'],
                'maintenancehistory': ['view', 'add', 'change']
            },
            'Deck Crew': {
                'equipment': ['view'],
                'maintenancetask': ['view'],
                'maintenancehistory': ['view', 'add'],
                'crewcertificate': ['view'],
                'certificatenotification': ['view']
            },
            'Engine Crew': {
                'equipment': ['view'],
                'maintenancetask': ['view'],
                'maintenancehistory': ['view', 'add'],
                'crewcertificate': ['view'],
                'certificatenotification': ['view']
            }
        }

        # Get content types
        content_types = {
            'crew': ContentType.objects.get_for_model(Crew),
            'crewcertificate': ContentType.objects.get_for_model(CrewCertificate),
            'certificatenotification': ContentType.objects.get_for_model(CertificateNotification),
            'equipment': ContentType.objects.get_for_model(Equipment),
            'maintenancetask': ContentType.objects.get_for_model(MaintenanceTask),
            'maintenancehistory': ContentType.objects.get_for_model(MaintenanceHistory)
        }

        # Create groups and assign permissions
        for group_name, permissions in group_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f'Created group: {group_name}')
            
            # Clear existing permissions
            group.permissions.clear()
            
            # Add new permissions
            for model, actions in permissions.items():
                for action in actions:
                    codename = f'{action}_{model}'
                    try:
                        permission = Permission.objects.get(
                            content_type=content_types[model],
                            codename=codename
                        )
                        group.permissions.add(permission)
                        self.stdout.write(f'Added permission {codename} to {group_name}')
                    except Permission.DoesNotExist:
                        self.stdout.write(f'Warning: Permission {codename} does not exist')

        self.stdout.write(self.style.SUCCESS('Successfully set up crew groups and permissions')) 