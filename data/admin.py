from django.contrib import admin
from models import UserCurrentHolding, UserDisplayHolding, Holding, HoldingPrice, HoldingAssetBreakdown, HoldingExpenseRatio

admin.site.register(UserCurrentHolding)
admin.site.register(UserDisplayHolding)
admin.site.register(Holding)
admin.site.register(HoldingPrice)
admin.site.register(HoldingAssetBreakdown)
admin.site.register(HoldingExpenseRatio)
