from django.contrib import admin
from data.models import *
# Register your models here.
admin.site.register(UserData)
admin.site.register(Holding)
admin.site.register(Security)
admin.site.register(SecurityPrice)
admin.site.register(YodleeAccount)
admin.site.register(AccountAmountDue)
admin.site.register(AnnuityBalance)
admin.site.register(InvestmentOption)