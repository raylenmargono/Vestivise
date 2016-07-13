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
from router import router
from django.views.generic import TemplateView

yodleeAPI = [
    url(r'^api/yodlee/appToken/$', yodleeViews.getAppToken, name='appToken'),
    url(r'^api/yodlee/accessToken/$', yodleeViews.getAccessToken, name='accessToken'),
    url(r'^api/yodlee/fastLinkToken/$', yodleeViews.getFastLinkToken, name='fastLinkToken'),
    url(r'^api/yodlee/fastLinkiFrame/$', yodleeViews.getFastLinkiFrame, name='fastLinkiFrame'),
]

userAPI = [
    url(r'^api/user/register/$', accountViews.register, name='register'),
    url(r'^api/user/login/$', accountViews.login, name='login'),

]

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^dashboard/$', dashboardViews.dashboard, name='dashboard'),
    url(r'^linkAccount/$', dashboardViews.linkAccountPage, name='linkAccount'),
    url(r'^login/$', accountViews.loginPage, name='loginPage'),
    url(r'^register/$', accountViews.signUpPage, name='signUpPage'),
]

urlpatterns+= router.urls
urlpatterns+= yodleeAPI
urlpatterns+= userAPI
urlpatterns+= [url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse')]
