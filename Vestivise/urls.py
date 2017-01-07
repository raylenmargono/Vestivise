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
from django.views.generic import TemplateView
from django.conf import settings
from dashboard import views as dashboardViews
from data import views as dataViews, tasks
from humanResources import views as humanResourceViews
from router import router
from django_js_reverse import views as reverse_views
from django.conf.urls.static import static
from webhooks import githook
from config import allowed_hosts

userAPI = [
    url(r'^api/user/register/$', dashboardViews.register, name='register'),
    url(r'^api/user/login/$', dashboardViews.login, name='login'),
    url(r'^api/user/profile/$', dashboardViews.UserProfileView.as_view(), name='profile'),
    url(r'^api/user/linkurl/$', dashboardViews.get_iframe_widget, name='quovoLinkUrl'),
    url(r'^api/user/test/nightlyProcess', dataViews.testNightlyProcess, name='testNightlyProcess'),
]

testAPI = [
    url(r'^api/demo/user/profile/$', dashboardViews.dashboardTestData, name='demoProfile')
]

dataAPI = [
    url(r'^api/data/(?P<module>[a-zA-Z]+)/$', dataViews.broker, name='broker'),
    url(r'^api/data/demo/(?P<module>[a-zA-Z]+)/$', dataViews.demoBroker, name='demoData'),
    # url(r'^api/holdings/$', dataViews.HoldingMetaDataListView.as_view(), name='holdings'),
    # url(r'^api/holdings/(?P<pk>[0-9]+)/$', dataViews.HoldingMetaDataDetailView.as_view(), name='holdingDetail')
]

hrAPI = [
    url(r'^api/hr/employees/create/csv/$', humanResourceViews.add_employees_using_csv, name='employeeCreateCSV'),
    url(r'^api/user/admin/login/$', humanResourceViews.login, name='hrLogin'),
    url(r'^api/user/admin/me/$', humanResourceViews.HumanResourceUserViewSet.as_view({'get': 'retrieve'}), name='hrMe'),
    url(r'api/user/admin/invite/$', humanResourceViews.resend_user_creation_email, name='reinviteUser')
]

urlpatterns = [
    url(r'^$', dashboardViews.homeRouter, name='home'),
    url(r'^vestiadmin/', admin.site.urls),
    url(r'^admin/login$', humanResourceViews.humanResourceLoginPage, name='humanResourceLoginPage'),
    url(r'^admin/', humanResourceViews.humanResourceAdminPage, name='humanResourceDashboard'),
    url(r'^dashboard/link/$', dashboardViews.linkAccountPage, name='linkAccountPage'),
    url(r'^accounts/sync/completed/$', dataViews.finishSyncHandler, name='sync_finish_handler'),
    url(r'^dashboard/$', dashboardViews.dashboard, name='dashboard'),
    url(r'^login/$', dashboardViews.loginPage, name='loginPage'),
    url(r'^logout/$', dashboardViews.logout, name='logout'),
    url(r'^register/(?P<magic_link>[\w\d]+)/$', dashboardViews.signUpPage, name='signUpPage'),
    url(r'^data/holdings/edit$', dataViews.holdingEditor, name='holdingEditorPage'),
    url(r'^demo/$', dashboardViews.demo, name='demo'),
    url(r'^subscribe/saleslead$', dashboardViews.subscribeToSalesList, name='subscribeToSalesList'),
    url(r'^services/git/KJKLSADJFKLSAF/IO0I0J/7329847892134/$', githook.git_post_receive, name='post-receive')
]

urlpatterns+= userAPI
urlpatterns+= testAPI
urlpatterns+= dataAPI
urlpatterns+= hrAPI
urlpatterns+= router.urls
urlpatterns+= [url(r'^jsreverse/$', reverse_views.urls_js, name='js_reverse')]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if allowed_hosts == "staging.vestivise.com":
    urlpatterns += [url(r'^services/np/$', tasks.nightly_process_proxy, name='np')]
