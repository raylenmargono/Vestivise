from django.contrib import admin
from models import UserCurrentHolding, UserDisplayHolding, \
    Holding, HoldingPrice, HoldingAssetBreakdown, HoldingExpenseRatio, \
    UserReturns, HoldingReturns, Transaction, AverageUserSharpe, UserSharpe, AverageUserReturns

admin.site.register(UserCurrentHolding)
admin.site.register(UserDisplayHolding)
admin.site.register(Holding)
admin.site.register(HoldingPrice)
admin.site.register(HoldingAssetBreakdown)
admin.site.register(HoldingExpenseRatio)
admin.site.register(UserReturns)
admin.site.register(HoldingReturns)
admin.site.register(Transaction)
admin.site.register(AverageUserSharpe)
admin.site.register(AverageUserReturns)
admin.site.register(UserSharpe)

