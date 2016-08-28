from django.test import TestCase
from thomson.apis import Instance as trapi
import datetime as dt

class thomsonReutersResponseTests(TestCase):

	def setUp(self):
		if not trapi.token:
			trapi.requestToken()
		self.assertNotEqual(trapi.token, '')

	def test_get_security_history(self):
		securities = [('AAPL.OQ', 'Ric'), ('438516AC0', 'Cusip'), ('AAPL', 'Sym')]
		start = dt.date.today() - dt.timedelta(days=30)
		res = trapi.securityHistory(securities, start, dt.date.today())
		if res.status_code != 200:
			print res.status_code
		self.assertEqual(res.status_code, 200)
		print
		try:
			jres = res.json()
			print jres
		except:
			print res.text

	def test_get_expense_ratio(self):
		securities = [('693391245', 'Cusip')]
		res = trapi.securityExpenseRatio(securities)
		if res.status_code != 200:
			print res.status_code
			print res.text
		self.assertEqual(res.status_code, 200)
		print
		try:
			jres = res.json()
			print jres
		except:
			print res.text