from rest_framework import routers
from humanResources.views import EmployeeManagementViewSet

router = routers.SimpleRouter()
router.register(r'api/hr/employees', EmployeeManagementViewSet, base_name='companyEmployeeManagement')

