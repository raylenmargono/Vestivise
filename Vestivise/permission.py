from rest_framework import permissions


class YodleeAccountOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        try:
            return request.user.profile.data.yodleeAccounts.filter(accountID=obj.accountID).first() != None
        except:
            return False
