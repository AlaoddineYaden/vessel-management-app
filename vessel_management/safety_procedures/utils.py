import re
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings


def generate_next_version(current_version):
    """Generate the next version number based on semantic versioning"""
    # Check if using semantic versioning (x.y.z)
    semver_match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', current_version)
    if semver_match:
        major, minor, patch = map(int, semver_match.groups())
        return f"{major}.{minor}.{patch + 1}"
    
    # Check if using major.minor (x.y)
    minver_match = re.match(r'^(\d+)\.(\d+)$', current_version)
    if minver_match:
        major, minor = map(int, minver_match.groups())
        return f"{major}.{minor + 1}"
    
    # Check if it's a simple number
    if current_version.isdigit():
        return str(int(current_version) + 1)
    
    # If it's a complex or custom version format, just append .1
    return f"{current_version}.1"