from rest_framework import permissions
from humanResources.models import SetUpUser

class QuovoAccountPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        if not request.user.is_authenticated():
            return False
        return request.user.profile.get_quovo_user()

class RegisterPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if "setUpUserID" not in request.POST:
            return False
        return SetUpUser.objects.filter(id=request.POST["setUpUserID"]).exists()

