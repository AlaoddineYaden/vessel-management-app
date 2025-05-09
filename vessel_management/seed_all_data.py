import os
import sys
import django
from django.core.management import call_command
from django.core.management.base import CommandError

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

def run_command(command_name):
    """Run a management command and handle errors"""
    try:
        print(f"\n{'='*50}")
        print(f"Running {command_name}...")
        print(f"{'='*50}\n")
        call_command(command_name)
        print(f"\n✓ Successfully completed {command_name}\n")
    except CommandError as e:
        print(f"\n✗ Error running {command_name}: {str(e)}\n")
    except Exception as e:
        print(f"\n✗ Unexpected error in {command_name}: {str(e)}\n")

def main():
    """Main function to run all commands"""
    setup_django()
    
    # List of all management commands to run
    commands = [
        'add_crew_data',
        'add_safety_data',
        'add_nc_data',
        'add_ism_data',
        'add_reporting_data',
        'add_pms_data'
    ]
    
    print("\nStarting data seeding process...")
    print("This will populate the database with sample data for all modules.")
    print("Make sure you have run migrations and created a vessel first!\n")
    
    # Run each command in sequence
    for command in commands:
        run_command(command)
    
    print("\nData seeding process completed!")
    print("Please check the output above for any errors.")

if __name__ == '__main__':
    main() 