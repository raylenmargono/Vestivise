from rest_framework import routers
from account.views import *

router = routers.SimpleRouter()
router.register(r'api/profile', UserProfileViewSet.as_view(), base_name='profile')