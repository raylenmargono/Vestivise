from django.contrib import admin
from account.views import *

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(BasicAccount)
admin.site.register(AccountModule)
