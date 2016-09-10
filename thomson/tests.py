from django.test import TestCase
import thomson.apis as trapi
import datetime as dt

class ThomsonReutersResponseTests(TestCase):

	def setUp(self):
		if not trapi.token:
			trapi.requestToken()
		self.assertNotEqual(trapi.token, '')

	def test_get_security_history(self):
		securities = [('AAPL.OQ', 'Ric'), ('PFOAX.O', 'Ric')]
		start = dt.date.today() - dt.timedelta(days=365)
		res = trapi.securityHistory(securities, start, dt.date.today())
		print(res)

	def test_get_security_returns(self):
		securities = [('AAPL.OQ', 'Ric'), ('PFOAX.O', 'Ric')]
		start = dt.date.today() - dt.timedelta(days=365)
		res = trapi.securityReturns(securities, start, dt.date.today())
		print(res.mean())
		print
		print(res.cov())

	def test_get_sharpe(self):
		securities = [('AAPL.OQ', 'Ric'), ('PFOAX.O', 'Ric')]
		start = dt.date.today() - dt.timedelta(days=365)
		sr = trapi.sharpeRatio([.5, .5], securities, start, dt.date.today())
		print(sr)

	def test_get_expense_ratio(self):
		securities = [('693391245', 'Cusip'), ('36239R503', 'Cusip'), ('09251T509', 'Cusip')]
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

	def test_get_fund_allocation(self):
		securities = [('693391245', 'Cusip')] #, ('36239R503', 'Cusip'), ('09251T509', 'Cusip')]
		res = trapi.fundAllocation(securities)
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
