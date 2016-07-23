from django.db import models
from django.contrib.auth.models import User
import json
# Create your models here.
#### USER DATA MODELS
class UserData(models.Model):

	user = models.OneToOneField(
		User,
		related_name='data',
		)
	class Meta:
		verbose_name = "UserData"
		verbose_name_plural = "UserData"

	def __str__(self):
		return "%s %s" % (self.user.profile.firstName, self.user.profile.lastName)


class holding(models.Model):
	portfolio = models.ForeignKey(
		UserData,
		on_delete=models.CASCADE,
		)
	cusip = models.CharField(max_length=9)
	holdingType = models.CharField(max_length = 20)
	price = models.PositiveIntegerField()
	priceCurrency = models.CharField(max_length=3)
	quantity = models.PositiveIntegerField()
	symbol = models.CharField(max_length=5)
	allocation = models.DecimalField(max_digits = 9, decimal_places=6)

	def __str__(self):
		return "%s - %s" % (self.holdingType, self.symbol )


class stock(models.Model):
	symbol = models.CharField(max_length=5, primary_key=True)
	lastUpdated = models.DateField()

	def __str__(self):
		return self.symbol

class stockPrice(models.Model):
	stock = models.ForeignKey(
		stock,
		on_delete=models.CASCADE,
		)
	date = models.DateField()
	price = models.DecimalField(max_digits=11, decimal_places=6)

	def __str__(self):
		return "%s %s" % (self.stock.symbol, str(self.date))
