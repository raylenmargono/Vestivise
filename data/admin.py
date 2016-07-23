from django.contrib import admin
from data.views import *
# Register your models here.
admin.site.register(UserData)
admin.site.register(holding)
admin.site.register(stock)
admin.site.register(stockPrice)