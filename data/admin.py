from django.contrib import admin
from models import UserCurrentHolding, UserDisplayHolding, \
    Holding, HoldingPrice, HoldingAssetBreakdown, HoldingExpenseRatio, \
    UserReturns, HoldingReturns, Transaction, AverageUserSharpe, UserSharpe, AverageUserReturns, HoldingJoin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

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
            queryset = queryset.exclude(ticker = None)
        else:
            queryset = queryset.filter(ticker = None)
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