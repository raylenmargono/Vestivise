from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    birthday = models.DateField()
    state = models.CharField(max_length=5)
    createdAt = models.DateField(auto_now_add=True)
    user = models.OneToOneField(User, related_name='profile')
    company = models.CharField(max_length=50)
    riskTolerence = models.CharField(max_length=50)

    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"

    def __str__(self):
        return "%s" % (self.user.email, )


class Module(models.Model):

    categories = (
        ('Risk', 'Risk'),
        ('Return', 'Return'),
        ('Asset', 'Asset'),
        ('Cost', 'Cost'),
    )

    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, choices=categories)
    endpoint = models.CharField(max_length=50)
    moduleID = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"

    def __str__(self):
        return self.moduleName


class QuovoUser(models.Model):

    quovoID = models.IntegerField()
    value = models.IntegerField(default=0)
    isCompleted = models.BooleanField(default=False)
    userProfile = models.ForeignKey('UserProfile')

    class Meta:
        verbose_name = "QuovoUser"
        verbose_name_plural = "QuovoUsers"

    def __str__(self):
        return "%s" % (self.userProfile.user.email, )

    def getNewHoldings(self):
        """
        Gathers the new holdings JSON from a call to the Quovo API.
        :return: A Json of the user's most recent holdings.
        """
        pass

    def setCurrHoldings(self, newHoldings):
        """
        Accepts a Json of new holdings and sets the UserCurretHoldings
        of this user to contain the values of the newHoldings.
        """
        pass

    def hasIncompleteHoldings(self):
        """
        Scans through the UserCurrentHoldings associated with the
        QuovoUser and determines whether or not they are all complete.
        :return: Boolean value denoting whether or not all the holdings
        associated with this QuovoUser are complete.
        """
        pass

    def updateDispHoldings(self):
        """
        Copies the values of the UserCurrentHoldings to the
        UserDisplayHoldings.
        """
