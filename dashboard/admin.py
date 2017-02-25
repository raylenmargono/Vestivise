from django.contrib import admin
from models import UserProfile, QuovoUser, Module, RecoveryLink, ProgressTracker



class UserProfileAdmin(admin.ModelAdmin):

    def did_link(self, instance):
        return instance.progress.did_link

    def complete_identification(self, instance):
        return instance.progress.did_link

    def dashboard_data_shown(self, instance):
        return instance.progress.did_link

    def did_open_dashboard(self, instance):
        return instance.progress.did_open_dashboard

    def accounts_linked(self, instance):
        pass

    def accounts_opened(self, instance):
        pass

    def contributions_since_retirement(self, instance):
        pass

    def change_in_user_holdings(self, instance):
        pass

    def dashboard_views(self, instance):
        pass

    def annotation_views(self, instance):
        pass

    def annotation_hovers(self, instance):
        pass

    def change_in_fees(self, instance):
        pass

    def module_hovers(self, instance):
        pass

    def dashboard_view_time(self, instance):
        pass

    def filter_count(self, instance):
        pass

    def tutorial_time(self, instance):
        pass


    list_display = ("user", "createdAt", "did_link", "complete_identification", "did_open_dashboard", "dashboard_data_shown")

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(QuovoUser)
admin.site.register(Module)
admin.site.register(RecoveryLink)
