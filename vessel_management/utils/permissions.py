
# 12. utils/permissions.py
from rest_framework import permissions
from authentication.models import User

class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow admin users to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == User.Role.ADMIN

class IsFleetManager(permissions.BasePermission):
    """
    Permission to only allow fleet managers to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == User.Role.FLEET_MANAGER

class IsCrew(permissions.BasePermission):
    """
    Permission to only allow crew members to access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == User.Role.CREW_MEMBER
