from django.contrib import admin
from models import UserProfile, QuovoUser, Module, RecoveryLink

admin.site.register(UserProfile)
admin.site.register(QuovoUser)
admin.site.register(Module)
admin.site.register(RecoveryLink)
