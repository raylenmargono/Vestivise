from rest_framework import routers
from landing.views import *
from dashboard.views import *

router = routers.SimpleRouter()
router.register(r'api/email', EmailViewSet)
router.register(r'api/referal', ReferalViewSet)
router.register(r'api/profile', UserProfileViewSet.as_view(), base_name='profile')