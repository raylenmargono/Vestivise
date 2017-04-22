from datetime import datetime, timedelta
from django.contrib import admin
from django import forms
from models import (
    UserCurrentHolding, UserDisplayHolding, HoldingPrice, HoldingAssetBreakdown, HoldingEquityBreakdown,
    AccountReturns, TreasuryBondValue, UserBondEquity, AverageUserFee, UserHistoricalHolding, Portfolio,
    Account, UserSharpe, AverageUserReturns, AverageUserSharpe, Transaction, HoldingReturns, HoldingExpenseRatio,
    HoldingBondBreakdown,
    HoldingJoin, Holding, UserFee, Benchmark, BenchmarkComposite)
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.db.models import Q
from Vestivise.morningstar import Morningstar, MorningstarRequestError

admin.site.register(UserCurrentHolding)
admin.site.register(UserDisplayHolding)
admin.site.register(HoldingPrice)
admin.site.register(HoldingAssetBreakdown)
admin.site.register(HoldingEquityBreakdown)
admin.site.register(HoldingBondBreakdown)
admin.site.register(HoldingExpenseRatio)
admin.site.register(HoldingReturns)
admin.site.register(Transaction)
admin.site.register(AverageUserSharpe)
admin.site.register(AverageUserReturns)
admin.site.register(UserSharpe)
admin.site.register(Account)
admin.site.register(Portfolio)
admin.site.register(UserHistoricalHolding)
admin.site.register(AverageUserFee)
admin.site.register(UserBondEquity)
admin.site.register(TreasuryBondValue)
admin.site.register(AccountReturns)
admin.site.register(UserFee)
admin.site.register(BenchmarkComposite)


class BenchmarkCompositeInline(admin.TabularInline):
    model = BenchmarkComposite


class BenchmarkAdmin(admin.ModelAdmin):
    inlines = [
        BenchmarkCompositeInline
    ]

admin.site.register(Benchmark, BenchmarkAdmin)


class HoldingFilter(admin.SimpleListFilter):

    title = 'is completed'
    parameter_name = 'ticker'

    def lookups(self, request, model_admin):

        result = [
            ("completed", "Completed"),
            ("incompleted", "Incompleted"),
            ("si", "Should Ignore"),
            ("is", "Other Sector")
        ]


        return result

    def queryset(self, request, queryset):
        if self.value() == "completed":
            queryset = queryset.exclude(
                  (Q(ticker = None) | Q(ticker = ""))
                & (Q(cusip = None) | Q(cusip = ""))
                & (Q(mstarid = None) | Q(mstarid = ""))
                & Q(category="CASH")
            )
        elif self.value() == "incompleted":
            queryset = queryset.filter(
                  (Q(ticker=None) | Q(ticker=""))
                & (Q(cusip=None) | Q(cusip=""))
                & (Q(mstarid=None) | Q(mstarid=""))
                & ~Q(category="CASH")
            )
        elif self.value() == "si":
            queryset = queryset.filter(
                category='IGNO'
            )
        elif self.value() == "is":
            queryset = queryset.filter(
                sector='Other'
            )
        return queryset



class HoldingResource(resources.ModelResource):

    class Meta:
        model = Holding

class HoldingJoinResource(resources.ModelResource):

    class Meta:
        model = HoldingJoin

class HoldingAdminForm(forms.ModelForm):

    class Meta:
        model = Holding
        fields = '__all__'

    def clean(self):
        data = self.cleaned_data
        cusip = data.get("cusip")
        ticker = data.get("ticker")
        mstarid = data.get("mstarid")
        category = data.get("category")
        ms = Morningstar
        end_date = datetime.now()
        start_date = datetime.now() - timedelta(weeks=1)

        is_identified = not(not cusip and not ticker and not mstarid)
        # check if should ignore
        if (category == "IGNO" or category == "CASH" or category == "FOFF") and is_identified:
            raise forms.ValidationError("A holding that is identified cannot be ignored")
        # check if filled out fields work
        if (category != "IGNO" and category != "CASH" and category != "FOFF") and not is_identified:
            raise forms.ValidationError("Fill out either cusip, ticker, or mstarid if not ignored")

        if category == "MUTF" and ticker:
            try:
                if not ms.getHistoricalNAV(ticker, "ticker", start_date, end_date):
                    raise forms.ValidationError("Use cusip for this Mutual funds/etf")
            except MorningstarRequestError:
                raise forms.ValidationError("Ticker is incorrect")

        method = None
        if category == "MUTF":
            method = ms.getHistoricalNAV
        if category == "STOC":
            method = ms.getHistoricalMarketPrice

        if method:
            if cusip:
                try:
                    if not method(cusip, "cusip", start_date, end_date):
                        raise forms.ValidationError("Cusip is incorrect")
                except:
                    raise forms.ValidationError("Cusip is incorrect")
            if ticker:
                try:
                    if not method(ticker, "ticker", start_date, end_date):
                        raise forms.ValidationError("Ticker is incorrect")
                except:
                    raise forms.ValidationError("Ticker is incorrect")
            if mstarid:
                if not method(mstarid, "mstarid", start_date, end_date):
                    raise forms.ValidationError("Morningstar id is incorrect")


@admin.register(Holding)
class HoldingAdmin(ImportExportModelAdmin):
    form = HoldingAdminForm
    resource_class = HoldingResource
    list_filter = (HoldingFilter,)
    list_display = ('secname', 'cusip', 'ticker', 'mstarid', 'sector', 'category')


@admin.register(HoldingJoin)
class HoldingJoinAdmin(ImportExportModelAdmin):
    resource_class = HoldingJoinResource