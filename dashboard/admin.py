from django.contrib import admin
from django.db.models import Sum
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from models import UserProfile, QuovoUser, Module, RecoveryLink, UserTracking, ProgressTracker


class UserProfileResource(resources.ModelResource):
    complete_identification = fields.Field()
    dashboard_data_shown = fields.Field()
    did_open_dashboard = fields.Field()
    accounts_linked = fields.Field()
    accounts_opened = fields.Field()
    contributions_since_creation = fields.Field()
    change_in_user_holdings = fields.Field()
    dashboard_views_time = fields.Field()
    annotation_views = fields.Field()
    on_hover_module = fields.Field()
    filter_count = fields.Field()
    tutorial_time = fields.Field()

    class Meta:
        model = UserProfile

    def dehydrate_complete_identification(self, instance):
        if hasattr(instance, "quovo_user"):
            return instance.quovo_user.has_completed_holding()
        return False

    def dehydrate_dashboard_data_shown(self, instance):
        return instance.progress.dashboard_data_shown

    def dehydrate_did_open_dashboard(self, instance):
        return instance.progress.did_open_dashboard

    def dehydrate_accounts_linked(self, instance):
        if hasattr(instance, "quovo_user"):
            return instance.quovo_user.user_accounts.exists()
        return 0

    def dehydrate_accounts_opened(self, instance):
        if hasattr(instance, "quovo_user") and instance.quovo_user.user_accounts.exists():
            return instance.quovo_user.user_accounts.all().count()
        return 0

    def dehydrate_contributions_since_creation(self, instance):
        if hasattr(instance, "quovo_user") and instance.quovo_user.user_transactions.exists():
            total = instance.quovo_user.get_contributions(acct_ignore=[]).filter(date__gte=instance.created_at)\
                            .aggregate(sum=Sum('value'))['sum']
            if total:
                return abs(total)
        return 0

    def dehydrate_change_in_user_holdings(self, instance):
        if hasattr(instance, "quovo_user") and instance.quovo_user.user_historical_holdings.exists():
            return instance.quovo_user.user_historical_holdings.latest('portfolio_index').portfolio_index - 1
        return 0

    def dehydrate_dashboard_views_time(self, instance):
        return instance.progress.total_dashboard_view_time

    def dehydrate_annotation_views(self, instance):
        return instance.progress.annotation_view_count

    def dehydrate_on_hover_module(self, instance):
        return instance.progress.hover_module_count

    def dehydrate_change_in_fees(self, instance):
        if hasattr(instance, "quovo_user") and instance.quovo_user.fees.exists():
            fees = instance.quovo_user.fees.all()
            return fees.latest('change_index').value - fees.earliest('change_index').value
        return 0

    def dehydrate_filter_count(self, instance):
        return instance.progress.total_filters

    def dehydrate_tutorial_time(self, instance):
        return instance.progress.tutorial_time


class UserProfileAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = UserProfileResource

    def complete_identification(self, instance):
        if hasattr(instance, "quovo_user"):
            return instance.quovo_user.has_completed_user_holdings()
        return False

    def dashboard_data_shown(self, instance):
        return instance.progress.dashboard_data_shown

    def did_open_dashboard(self, instance):
        return instance.progress.did_open_dashboard

    def accounts_linked(self, instance):
        return instance.quovo_user.user_accounts.exists()

    def accounts_opened(self, instance):
        if instance.quovo_user.user_accounts.exists():
            return instance.quovo_user.user_accounts.all().count()
        return 0

    def contributions_since_creation(self, instance):
        if instance.quovo_user.user_transaction.exists():
            total = instance.quovo_user.get_contributions(acct_ignore=[]).filter(date__gte=instance.created_at)\
                            .aggregate(sum=Sum('value'))['sum']
            if total:
                return abs(total)
        return 0

    def change_in_user_holdings(self, instance):
        if instance.quovo_user.user_historical_holdings.exists():
            return instance.quovo_user.user_historical_holdings.latest('portfolio_index').portfolio_index - 1
        return 0

    def dashboard_views_time(self, instance):
        return instance.progress.total_dashboard_view_time

    def annotation_views(self, instance):
        return instance.progress.annotation_view_count

    def on_hover_module(self, instance):
        return instance.progress.hover_module_count

    def change_in_fees(self, instance):
        if instance.quovo_user.fees.exists():
            fees = instance.quovo_user.fees.all()
            return fees.latest('change_index').value - fees.earliest('change_index').value
        return 0

    def filter_count(self, instance):
        return instance.progress.total_filters

    def tutorial_time(self, instance):
        return instance.progress.tutorial_time

    list_display = (
        "user",
        "created_at",
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


class UserTrackingResource(resources.ModelResource):

    class Meta:
        model = UserTracking


class UserTrackingAdmin(ImportExportModelAdmin):
    resource_class = UserTrackingResource

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(QuovoUser)
admin.site.register(Module)
admin.site.register(RecoveryLink)
admin.site.register(UserTracking, UserTrackingAdmin)
admin.site.register(ProgressTracker)
