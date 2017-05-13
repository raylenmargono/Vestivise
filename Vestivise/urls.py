"""Vestivise URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from dashboard import views as dashboard_views
from data import views as data_views, tasks
from humanResources import views as hr_views
from router import router
from django_js_reverse import views as reverse_views
from webhooks import githook
from config import allowed_hosts

userAPI = [
    url(r'^api/user/register/$', dashboard_views.register, name='register'),
    url(r'^api/user/me/update/$', dashboard_views.profile_update, name='profileUpdate'),
    url(r'^api/user/password/recovery/$', dashboard_views.password_recovery, name='passwordRecovery'),
    url(r'^api/user/password/reset/$', dashboard_views.password_reset, name='passwordReset'),
    url(r'^api/user/login/$', dashboard_views.login, name='login'),
    url(r'^api/user/profile/$', dashboard_views.UserProfileView.as_view(), name='profile'),
    url(r'^api/user/linkurl/$', dashboard_views.get_iframe_widget, name='quovoLinkUrl'),
    url(r'^api/user/test/nightlyProcess', data_views.testNightlyProcess, name='testNightlyProcess'),
]

testAPI = [
    url(r'^api/demo/user/profile/$', dashboard_views.dashboard_test_data, name='demoProfile')
]

dataAPI = [
    url(r'^api/data/(?P<module>[a-zA-Z]+)/$', data_views.broker, name='broker'),
    url(r'^api/data/demo/(?P<module>[a-zA-Z]+)/$', data_views.demoBroker, name='demoData'),
    url(r'^api/track/', dashboard_views.track_progress, name='progressTracker')
]

hrAPI = [
    url(r'^api/hr/employees/create/csv/$', hr_views.add_employees_using_csv, name='employeeCreateCSV'),
    url(r'^api/user/admin/login/$', hr_views.login, name='hrLogin'),
    url(r'^api/user/admin/me/$', hr_views.HumanResourceUserViewSet.as_view({'get': 'retrieve'}), name='hrMe'),
    url(r'api/user/admin/invite/$', hr_views.resend_user_creation_email, name='reinviteUser')
]

urlpatterns = [
    url(r'^$', dashboard_views.home_router, name='home'),
    url(r'^vestiadmin/', admin.site.urls),
    #url(r'^admin/login$', humanResourceViews.humanResourceLoginPage, name='humanResourceLoginPage'),
    #url(r'^admin/', humanResourceViews.humanResourceAdminPage, name='humanResourceDashboard'),
    url(r'^dashboard/settings/$', dashboard_views.settings_page, name='settingsPage'),
    url(r'^accounts/sync/completed/$', data_views.finishSyncHandler, name='sync_finish_handler'),
    url(r'^dashboard/$', dashboard_views.dashboard, name='dashboard'),
    url(r'^login/$', dashboard_views.login_page, name='loginPage'),
    url(r'^password/recovery(?:/(?P<link>[\w\d]+))?/$', dashboard_views.password_recovery_page_handler,
        name='passwordRecoveryPage'),
    url(r'^logout/dashboard/$', dashboard_views.logout, name='logout'),
    url(r'^logout/admin/$', hr_views.logout, name='logoutAdmin'),
    url(r'^register(?:/(?P<magic_link>[\w\d]+))?/$', dashboard_views.sign_up_page, name='signUpPage'),
    url(r'^data/holdings/edit$', data_views.holdingEditor, name='holdingEditorPage'),
    url(r'^demo/$', dashboard_views.demo, name='demo'),
    url(r'^subscribe/saleslead$', dashboard_views.subscribe_to_sales_list, name='subscribeToSalesList'),
    url(r'^services/git/KJKLSADJFKLSAF/IO0I0J/7329847892134/$', githook.git_post_receive, name='post-receive')
]

urlpatterns += userAPI
urlpatterns += testAPI
urlpatterns += dataAPI
urlpatterns += hrAPI
urlpatterns += router.urls
urlpatterns += [url(r'^jsreverse/$', reverse_views.urls_js, name='js_reverse')]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if allowed_hosts == "staging.vestivise.com":
    urlpatterns += [url(r'^services/np/$', tasks.nightly_process_proxy, name='np')]
