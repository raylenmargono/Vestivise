from __future__ import unicode_literals
from django.db import models
from account.models import *

# Create your models here.
class BasicDashboardAccount(models.Model):

    # model relationships
    # asset allocation
    # fund performance
    # risk 
    # fee comparison
    user = models.ForeignKey(UserProfile, related_name='account')

    class Meta:
        verbose_name = "BasicDashboardAccount"
        verbose_name_plural = "BasicDashboardAccounts"

    def __str__(self):
        pass