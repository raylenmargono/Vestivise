from django.contrib import admin
from data.views import *
# Register your models here.
admin.site.register(UserData)
admin.site.register(Holding)
admin.site.register(Stock)
admin.site.register(StockPrice)