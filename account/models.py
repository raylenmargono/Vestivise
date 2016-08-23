from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField

# Create your models here.

class UserProfile(models.Model):

    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    birthday = models.DateField()
    state = models.CharField(max_length=5)
    createdAt = models.DateField(auto_now_add=True)
    user = models.OneToOneField(User, related_name='profile')
    income = models.IntegerField()

    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"

    def __str__(self):
        return "%s %s" % (self.firstName, self.lastName)


class BasicAccount(models.Model):

    userProfile = models.OneToOneField("UserProfile", related_name='vest_account')
    linkedAccount = models.BooleanField(default=False)

    class Meta:
        verbose_name = "BasicAccount"
        verbose_name_plural = "BasicAccounts"

    def __str__(self):
        return self.userProfile.firstName


class AccountModule(models.Model):
    account = models.ForeignKey("BasicAccount", related_name='account_modules')
    module = models.ForeignKey("Module", related_name='modules')
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "AccountModule"
        verbose_name_plural = "AccountModules"
        ordering = ('createdAt', )

    def __str__(self):
        return "%s: %s" % (self.account, self.module.moduleName)


class Module(models.Model):

    moduleName = models.CharField(max_length=50)
    account = models.CharField(max_length=50)
    category = models.CharField(max_length=20)
    endpoint = models.CharField(max_length=20)
    chartType = models.CharField(max_length=50)
    moduleID = models.CharField(max_length=50)
    chartFormat = JSONField()

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Module"

    def __str__(self):
        return self.moduleName
