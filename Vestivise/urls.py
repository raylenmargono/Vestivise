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
from dashboard import views as dashboardViews
from data import views as dataViews
from django.views.generic import TemplateView
from humanResources import views as humanResourceViews

userAPI = [
    url(r'^api/user/register/$', dashboardViews.register, name='register'),
    url(r'^api/user/login/$', dashboardViews.login, name='login'),
    # url(r'^api/user/data/update/$', dataViews.update_user_data, name='updateData'),
    url(r'^api/user/profile/$', dashboardViews.UserProfileView.as_view(), name='profile'),
    # url(r'^api/user/profile/account$', dashboardViews.UserBasicAccountView.as_view(), name='account'),
    # url(r'^api/user/profile/account/linkedAccounts/$', dataViews.YodleeAccountList.as_view(), name='linkedAccountsList'),
    # url(r'^api/user/profile/account/linkedAccounts/(?P<accountID>[0-9]+)/$', dataViews.YodleeAccountDetail.as_view(), name='linkedAccountsDetail')
]

testAPI = [
    url(r'^test/user/account/$', dashboardViews.dashboardTestData, name='test_dashboardData'),
]

dataAPI = [
    url(r'^api/data/(?P<module>[a-zA-Z]+)/$', dataViews.broker, name='broker'),
    # url(r'^api/holdings/$', dataViews.HoldingMetaDataListView.as_view(), name='holdings'),
    # url(r'^api/holdings/(?P<pk>[0-9]+)/$', dataViews.HoldingMetaDataDetailView.as_view(), name='holdingDetail')
]

hrAPI = [
    url(r'^api/hr/employees/create/csv/$', humanResourceViews.add_employees_using_csv, name='employeeCreateCSV')
]

urlpatterns = [
    # url(r'^$', dashboardViews.homeRouter, name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/link/$', dashboardViews.get_iframe_widget, name='iframe_widget'),
    url(r'^accounts/sync/$', dataViews.finishSyncHandler, name='sync_finish_handler')
    # url(r'^dashboard/$', dashboardViews.dashboard, name='dashboard'),
    # url(r'^linkAccount/$', dashboardViews.linkAccountPage, name='linkAccount'),
    # url(r'^login/$', dashboardViews.loginPage, name='loginPage'),
    # url(r'^logout/$', dashboardViews.logout, name='logout'),
    # url(r'^register/$', dashboardViews.signUpPage, name='signUpPage'),
    # url(r'^data/update$', dashboardViews.dataUpdatePage, name='updateDataPage'),
    # url(r'^dashboard/options$', dashboardViews.optionsPage, name='optionsPage'),
    # url(r'^data/holdings/edit$', dataViews.holdingEditor, name='holdingEditorPage'),
    # url(r'^demo/$', TemplateView.as_view(template_name='dashboard/demo.html'), name='demo'),
    # url(r'^subscribe/saleslead$', dashboardViews.subscribeToSalesList, name='subscribeToSalesList')
]

urlpatterns+= userAPI
urlpatterns+= testAPI
urlpatterns+= dataAPI
urlpatterns+= hrAPI
urlpatterns+= [url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse')]
