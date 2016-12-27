from rest_framework import permissions

from dashboard.models import UserProfile


class HumanResourceWritePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        employee_id = request.PUT.get("employee_id")
        if employee_id or hasattr(request.user, 'humanResourceProfile'):
            try:
                employee = UserProfile.objects.get(id=employee_id)
                return employee.company == request.user.humanResourceProfile.company
            except UserProfile.DoesNotExist:
                return False
        return False


class HumanResourcePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return hasattr(request.user, 'humanResourceProfile')
