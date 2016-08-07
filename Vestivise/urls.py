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
from yodlee import views as yodleeViews
from account import views as accountViews
from data import views as dataViews
from Vestivise.router import router
from django.views.generic import TemplateView

yodleeAPI = [
    url(r'^api/yodlee/fastLinkToken/$', yodleeViews.getFastLinkToken, name='fastLinkToken'),
]

userAPI = [
    url(r'^api/user/register/$', accountViews.register, name='register'),
    url(r'^api/user/login/$', accountViews.login, name='login'),
    url(r'^api/user/data/update/$', dataViews.update_user_data, name='updateData'),
    url(r'^api/user/profile/$', accountViews.UserProfileView.as_view(), name='profile'),
    url(r'^api/user/profile/account$', accountViews.UserBasicAccountView.as_view(), name='account')

]

testAPI = [
    url(r'^test/user/account$', dashboardViews.dashboardTestData, name='test_dashboardData'),
]

dataAPI = [
    url(r'^api/data/(?P<module>[a-zA-Z]+)/$', dataViews.broker, name='broker'),
]

urlpatterns = [
    url(r'^$', dashboardViews.homeRouter, name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^dashboard/$', dashboardViews.dashboard, name='dashboard'),
    url(r'^linkAccount/$', dashboardViews.linkAccountPage, name='linkAccount'),
    url(r'^login/$', accountViews.loginPage, name='loginPage'),
    url(r'^logout/$', accountViews.logout, name='logout'),
    url(r'^register/$', accountViews.signUpPage, name='signUpPage'),
    url(r'^data/update$', dashboardViews.dataUpdatePage, name='updateDataPage')
]

urlpatterns+= router.urls
urlpatterns+= yodleeAPI
urlpatterns+= userAPI
urlpatterns+= testAPI
urlpatterns+= dataAPI
urlpatterns+= [url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse')]
