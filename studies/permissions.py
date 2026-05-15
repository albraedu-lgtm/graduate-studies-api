from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or request.user.groups.filter(name='GraduateAdmin').exists()
        )

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or request.user.groups.filter(name='GraduateAdmin').exists()
        )

class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or request.user.groups.filter(name='AcademicSupervisor').exists()
        )

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or request.user.groups.filter(name='GraduateStudent').exists()
        )

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.groups.filter(name='GraduateAdmin').exists():
            return True
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        if hasattr(obj, 'student') and obj.student == request.user:
            return True
        if hasattr(obj, 'supervisor') and obj.supervisor == request.user:
            return True
        if hasattr(obj, 'submitted_by') and obj.submitted_by == request.user:
            return True
        if hasattr(obj, 'author') and obj.author == request.user:
            return True
        return False
