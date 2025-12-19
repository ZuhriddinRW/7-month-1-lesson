from rest_framework.permissions import BasePermission, SAFE_METHODS

class CanReadComment(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated

class CanCreateComment(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            user = request.user
            return user.is_authenticated and not user.is_manager
        return True

class CanUpdateDeleteComment(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            user = request.user
            return user.is_authenticated and user.is_admin and not user.is_manager
        return True

class AdminNoUpdatePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if not request.user.is_authenticated or not request.user.is_admin:
            return False

        if request.method in ['PUT', 'PATCH']:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)