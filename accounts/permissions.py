from rest_framework import permissions

class IsRead(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False

class IsWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'POST']:
            return True
        return False

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return True
