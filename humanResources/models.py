from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class HumanResourceProfile(models.Model):
    company = models.CharField(max_length=100)
    user = models.OneToOneField(User, related_name='humanResourceProfile')
    is_roth = models.BooleanField(default=False)
    employee_estimate = models.IntegerField(default=0)

    def get_employee_ceiling(self):
        return float(self.employee_estimate) * 1.1

    class Meta:
        verbose_name = "HumanResourceProfile"
        verbose_name_plural = "HumanResourceProfiles"

    def __str__(self):
        return self.company

class SetUpUser(models.Model):

    email = models.EmailField(unique=True)
    company = models.CharField(max_length=100)
    magic_link = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    @staticmethod
    def deactivate_setupuser(setUpUserID):
        """
        Deletes SetUpUser
        :param setUpUserID: a setupuser id
        """
        user = SetUpUser.objects.get(id=setUpUserID)
        user.is_active = False
        user.save()

    class Meta:
        verbose_name = "SetUpUser"
        verbose_name_plural = "SetUpUsers"

    def __str__(self):
        return self.email
