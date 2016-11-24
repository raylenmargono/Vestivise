from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class HumanResourceProfile(models.Model):
    company = models.CharField(max_length=100)
    user = models.OneToOneField(User, related_name='humanResourceProfile')
    is_roth = models.BooleanField(default=False)

    class Meta:
        verbose_name = "HumanResourceProfile"
        verbose_name_plural = "HumanResourceProfiles"

    def __str__(self):
        return self.company


class SetUpUser(models.Model):

    email = models.EmailField()
    company = models.CharField(max_length=100)
    magic_link = models.CharField(max_length=100)

    @staticmethod
    def deleteSetupUser(setUpUserID):
        """
        Deletes SetUpUser
        :param setUpUserID: a setupuser id
        """
        SetUpUser.objects.get(id=setUpUserID).delete()

    class Meta:
        verbose_name = "SetUpUser"
        verbose_name_plural = "SetUpUsers"

    def __str__(self):
        return "%s: %s %s" % (self.first_name, self.last_name, self.company )
