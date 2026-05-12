from rest_framework import permissions  

"""Для пользователей"""
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj == request.user:
            return True
        return request.user.role.role_name == 'admin'

"""Общее"""
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role.role_name == 'admin'
    def has_object_permission(self, request, view, obj):
        return request.user.role.role_name == 'admin'
    
"""Для списков"""
class IsAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user