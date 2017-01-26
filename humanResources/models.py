from __future__ import unicode_literals

import django
from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4
from django.db import IntegrityError

# Create your models here.


class HumanResourceProfile(models.Model):
    company = models.CharField(max_length=100)
    user = models.OneToOneField(User, related_name='humanResourceProfile')
    is_roth = models.BooleanField(default=False)
    subscription_date = models.DateField(default=django.utils.timezone.now)

    class Meta:
        verbose_name = "HumanResourceProfile"
        verbose_name_plural = "HumanResourceProfiles"

    def __str__(self):
        return self.company

class SetUpUser(models.Model):

    id = models.CharField(primary_key=True, max_length=32)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=100)
    magic_link = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.id:
            super(SetUpUser, self).save(*args, **kwargs)
            return

        unique = False
        while not unique:
            try:
                self.id = uuid4().hex
                super(SetUpUser, self).save(*args, **kwargs)
            except IntegrityError:
                self.id = uuid4().hex
            else:
                unique = True

    def activate(self):
        self.is_active = True
        self.save()

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
