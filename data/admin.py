from django.contrib import admin
from models import UserCurrentHolding, UserDisplayHolding, \
    Holding, HoldingPrice, HoldingAssetBreakdown, HoldingExpenseRatio, \
    UserReturns, HoldingReturns, Transaction, AverageUserSharpe, UserSharpe, AverageUserReturns, HoldingJoin, Portfolio, \
    Account
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.db.models import Q

admin.site.register(UserCurrentHolding)
admin.site.register(UserDisplayHolding)
admin.site.register(HoldingPrice)
admin.site.register(HoldingAssetBreakdown)
admin.site.register(HoldingExpenseRatio)
admin.site.register(UserReturns)
admin.site.register(HoldingReturns)
admin.site.register(Transaction)
admin.site.register(AverageUserSharpe)
admin.site.register(AverageUserReturns)
admin.site.register(UserSharpe)
admin.site.register(Account)
admin.site.register(Portfolio)


class HoldingFilter(admin.SimpleListFilter):

    title = 'is completed'
    parameter_name = 'ticker'

    def lookups(self, request, model_admin):

        result = [
            ("completed", "Completed"),
            ("incompleted", "Incompleted")
        ]


        return result

    def queryset(self, request, queryset):
        if self.value() == "completed":
            queryset = queryset.exclude(
                  (Q(ticker = None) | Q(ticker = ""))
                & (Q(cusip = None) | Q(cusip = ""))
                & (Q(mstarid = None) | Q(mstarid = ""))
                & Q(shouldIgnore=False)
            )
        elif self.value() == "incompleted":
            queryset = queryset.filter(
                  (Q(ticker=None) | Q(ticker=""))
                & (Q(cusip=None) | Q(cusip=""))
                & (Q(mstarid=None) | Q(mstarid=""))
                & Q(shouldIgnore=False)
            )
        return queryset



class HoldingResource(resources.ModelResource):

    class Meta:
        model = Holding

class HoldingJoinResource(resources.ModelResource):

    class Meta:
        model = HoldingJoin

@admin.register(Holding)
class HoldingAdmin(ImportExportModelAdmin):
    resource_class = HoldingResource
    list_filter = (HoldingFilter,)

@admin.register(HoldingJoin)
class HoldingJoinAdmin(ImportExportModelAdmin):
    resource_class = HoldingJoinResource