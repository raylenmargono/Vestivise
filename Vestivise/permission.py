import hmac
from hashlib import sha1
from rest_framework import permissions
from humanResources.models import SetUpUser
from keys import quovo_webhook_secret

class QuovoAccountPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        if not request.user.is_authenticated() or not hasattr(request.user, "profile"):
            return False
        return request.user.profile.get_quovo_user()


class RegisterPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if "setUpUserID" not in request.POST:
            return False
        return SetUpUser.objects.filter(id=request.POST["setUpUserID"]).exists()

class QuovoWebHookPermission(permissions.BasePermission):

    def verify_payload(self, payload, signature, secret=quovo_webhook_secret):
        hashed = hmac.new(secret, payload, sha1)
        return hmac.compare_digest(hashed.hexdigest(), signature)

    def has_permission(self, request, view):
        signature = request.META.get("HTTP_WEBHOOK_SIGNATURE")
        if not request.body or not signature: return False
        return self.verify_payload(request.body, signature)


class HumanResourcePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated() or not hasattr(request.user, "humanResourceProfile"):
            return True
        return False

