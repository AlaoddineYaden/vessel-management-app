# audit_inspection/permissions.py

from rest_framework import permissions


class IsAuditorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow auditors to edit audits.
    Read permissions are allowed to authenticated users.
    """
    
    def has_permission(self, request, view):
        # Allow read access to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions only for users with auditor role
        # Assuming the User model has an is_auditor field or method
        return request.user.is_authenticated and (
            request.user.is_staff or 
            hasattr(request.user, 'is_auditor') and request.user.is_auditor
        )


class IsInspectorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow inspectors to edit inspections.
    Read permissions are allowed to authenticated users.
    """
    
    def has_permission(self, request, view):
        # Allow read access to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions only for users with inspector role
        # Assuming the User model has an is_inspector field or method
        return request.user.is_authenticated and (
            request.user.is_staff or 
            hasattr(request.user, 'is_inspector') and request.user.is_inspector
        )
