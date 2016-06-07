from __future__ import unicode_literals

from django.db import models
from datetime import datetime
# Create your models here.


class Email(models.Model):
    email = models.EmailField(unique=True)
    createdAt = models.DateTimeField(default=datetime.now, blank=True)
    acceptedEmails = models.IntegerField(default=0)


class Referal(models.Model):
    email = models.EmailField()
    createdAt = models.DateTimeField(default=datetime.now, blank=True)
    refree = models.ForeignKey(Email)
    accepted = models.BooleanField(default=False)
