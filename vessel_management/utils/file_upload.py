# 14. utils/file_upload.py
import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.exceptions import ValidationError

def validate_file_extension(file):
    """
    Validate if the file extension is allowed.
    """
    ext = os.path.splitext(file.name)[1][1:].lower()
    if ext not in settings.ALLOWED_FILE_TYPES:
        raise ValidationError(f"Unsupported file extension: {ext}. Allowed extensions are: {', '.join(settings.ALLOWED_FILE_TYPES)}")
    return True

def validate_file_size(file):
    """
    Validate if the file size is within limit.
    """
    if file.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        max_size_mb = settings.FILE_UPLOAD_MAX_MEMORY_SIZE / (1024 * 1024)
        raise ValidationError(f"File size exceeds maximum allowed size: {max_size_mb} MB")
    return True

def handle_uploaded_file(file, folder='documents/'):
    """
    Process an uploaded file:
    1. Validate file extension and size
    2. Generate a unique filename
    3. Save the file to storage
    4. Return the file path
    """
    # Validate file
    validate_file_extension(file)
    validate_file_size(file)
    
    # Generate unique filename to avoid overwriting
    filename = file.name
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{uuid.uuid4().hex}{ext}"
    
    # Construct the file path
    file_path = os.path.join(folder, unique_filename)
    
    # Save file to storage
    path = default_storage.save(file_path, file)
    
    # Return the file URL
    return path

def get_file_url(file_path):
    """
    Generate a URL for accessing the file.
    """
    if not file_path:
        return None
    
    return os.path.join(settings.MEDIA_URL, file_path)
