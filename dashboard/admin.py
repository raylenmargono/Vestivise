from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from models import UserProfile, QuovoUser, Module, RecoveryLink
from django.db.models import Sum


class UserProfileResource(resources.ModelResource):

    class Meta:
        model = UserProfile

class UserProfileAdmin(ImportExportModelAdmin):
    resource_class = UserProfileResource

    def did_link(self, instance):
        return instance.progress.did_link

    def complete_identification(self, instance):
        return instance.progress.did_link

    def dashboard_data_shown(self, instance):
        return instance.progress.dashboard_data_shown

    def did_open_dashboard(self, instance):
        return instance.progress.did_open_dashboard

    def accounts_linked(self, instance):
        return instance.quovoUser.userAccounts.exists()

    def accounts_opened(self, instance):
        if instance.quovoUser.userAccounts.exists():
            return instance.quovoUser.userAccounts.all().count()
        return 0

    def contributions_since_creation(self, instance):
        if instance.quovoUser.userTransaction.exists():
            return abs(instance.quovoUser.getContributions().filter(date__gte=instance.createdAt).aggregate(sum=Sum('value'))['sum'])
        return 0

    def change_in_user_holdings(self, instance):
        if instance.quovoUser.userHistoricalHoldings.exists():
            return instance.quovoUser.userHistoricalHoldings.latest('portfolioIndex').portfolioIndex - 1
        return 0

    def dashboard_views_time(self, instance):
        return instance.progress.total_dashboard_view_time

    def annotation_views(self, instance):
        return instance.progress.annotation_view_count

    def on_hover_module(self, instance):
        return instance.progress.hover_module_count

    def change_in_fees(self, instance):
        if instance.quovoUser.fees.exists():
            fees = instance.quovoUser.fees.all()
            return fees.latest('changeIndex').value - fees.earliest('changeIndex').value
        return 0

    def filter_count(self, instance):
        return instance.progress.total_filters

    def tutorial_time(self, instance):
        return instance.progress.tutorial_time


    list_display = (
        "user",
        "createdAt",
        "did_link",
        "complete_identification",
        "did_open_dashboard",
        "dashboard_data_shown",
        "accounts_linked",
        "accounts_opened",
        "dashboard_views_time",
        "annotation_views",
        "on_hover_module",
        "filter_count",
        "tutorial_time",
        'contributions_since_creation',
        'change_in_user_holdings',
        'change_in_fees'
    )

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(QuovoUser)
admin.site.register(Module)
admin.site.register(RecoveryLink)
