from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """Permission for SuperAdmin only"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'SUPERADMIN'

class IsTeacher(permissions.BasePermission):
    """Permission for Teacher only"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'TEACHER'

class IsAccountant(permissions.BasePermission):
    """Permission for Accountant only"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ACCOUNTANT'

class IsSuperAdminOrAccountant(permissions.BasePermission):
    """Permission for SuperAdmin or Accountant"""
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.role in ['SUPERADMIN', 'ACCOUNTANT'])