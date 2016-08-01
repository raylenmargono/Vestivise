from django.contrib import admin
from data.models import *
# Register your models here.
admin.site.register(UserData)
admin.site.register(Holding)
admin.site.register(Stock)
admin.site.register(StockPrice)
admin.site.register(YodleeAccount)
admin.site.register(AccountAmountDue)
admin.site.register(AnnuityBalance)