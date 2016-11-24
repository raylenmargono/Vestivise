from django.test import TestCase
from django.utils import timezone
from data.serializers import *
from data.models import *
from data import tasks
from dashboard.models import *
from django.contrib.auth.models import User

# Create your tests here.


class DataHoldingModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testUser')
        up = UserProfile.objects.create(
            user=self.user,
            firstName="testUser",
            lastName="lastname",
            birthday="2016-08-03",
            state="NY",
            company="Vestivise"
        )
        QuovoUser.objects.create(
            quovoID=0,
            userProfile=up
        )
        Holding.objects.create(
            secname="Target Retirement 2040 Trust II",
            cusip="92202V666",
            updatedAt=timezone.now()
        )
        Holding.objects.create(
            secname="Good Stuff Fund",
            updatedAt=timezone.now()
        )

    def test_getHoldingByPositionDict(self):
        res = Holding.getHoldingByPositionDict({"ticker_name": "Target Retirement 2040 Trust II"})
        self.assertEqual(res.cusip, "92202V666", "Asset could not be found by name!")

        newres = Holding.getHoldingByPositionDict({"ticker_name": "Mary's milk", "cusip": "000000000"})
        self.assertEqual(newres.secname, "Mary's milk", "New Holding has incorrect name!")
        self.assertEqual(newres.cusip, "000000000", "New Holding has incorrect cusip! Has cusip: " + str(newres.cusip))
        try:
            testget = Holding.objects.get(cusip="000000000")
        except Holding.DoesNotExist:
            self.assertTrue(False, "Newly created Holding cannot be found!")

    def test_getHoldingBySecname(self):
        res = Holding.getHoldingBySecname("Target Retirement 2040 Trust II")
        self.assertEqual(res.cusip, "92202V666", "Incorrect cusip on returned holding!")

        newres = Holding.getHoldingBySecname("Billy Bob's meats")
        self.assertTrue(hasattr(newres, "secname"), "Reference to new item has no secname while it should!")
        self.assertEqual(newres.cusip, None, "Reference to new item has incorrect cusip! Has cusip: " + str(newres.cusip))

    def test_isIdentified(self):
        vanguard = Holding.getHoldingBySecname("Target Retirement 2040 Trust II")
        self.assertTrue(vanguard.isIdentified(), "Holding is identified, but claimed it wasn't!")

        good = Holding.getHoldingBySecname("Good Stuff Fund")
        self.assertFalse(good.isIdentified(), "Holding isn't identified, but claimed it was!")


# class NightlyProcessTests(TestCase):
#     def setUp(self):
#         self.user = User.objects.create(username='testUser')
#         up = UserProfile.objects.create(
#             user=self.user,
#             firstName="testUser",
#             lastName="lastname",
#             birthday="2016-08-03",
#             state="NY",
#             company="Vestivise"
#         )
#         QuovoUser.objects.create(
#             quovoID=0,
#             userProfile=up
#         )

