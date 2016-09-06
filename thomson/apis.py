import requests
import json
import datetime
from Vestivise.keys import tr_username, tr_password

apiBase = 'https://hosted.datascopeapi.reuters.com/RestApi/v1/'

class ThomsonException(Exception):
	def __init__(self, dErrorArguments):
		Exception.__init__(self, dErrorArguments)

class Instance:
	token  = ''

	@staticmethod
	def requestToken():
		print("Obtaining thomson auth token")
		header = {
			'Prefer': 'respond-async',
			'Content-Type': 'application/json'
		}
		body = {
			'Credentials':{
				'Username': tr_username,
				'Password': tr_password
			}
		}
		res = requests.post(apiBase + 'Authentication/RequestToken', data=json.dumps(body), headers=header)
		try:
			if 'error' in res.json():
				raise ThomsonException(res.json()['error'])
			Instance.token = 'Token ' + res.json()['value']
		except ValueError:
			print "Timeout"
			print res.text

	@staticmethod
	def securityHistory(secList, startDate, endDate):
		'''
		secList should be structured as:
		[ (sec1, IdentifierType), (sec2, IdentifierType), ...]
		Also, note that startDate and endDate expect datetime.date
		objects, NOT datetimes.
		'''
		body = {
			'ExtractionRequest': {
				'@odata.type': '#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.TimeSeriesExtractionRequest',
				'ContentFieldNames': [
					'Close Price',
					'Trade Date',
					'Ticker'
				],
				'IdentifierList':{
					'@odata.type': '#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.InstrumentIdentifierList',
					'InstrumentIdentifiers': 
					[{'Identifier': s[0], 'IdentifierType':s[1]} for s in secList],

				},
				'Condition': {
					'StartDate': str(startDate) + "T00:00:00.000Z",
					'EndDate' : str(endDate) + "T00:00:00.000Z",
				}
			}
		}
		header = {
			'Prefer': 'respond-async',
			'Content-Type': 'application/json',
			'Authorization': Instance.token
		}

		res = requests.post(apiBase + 'Extractions/Extract', data=json.dumps(body), headers=header)
		try:
			if 'error' in res.json():
				raise ThomsonException(res.json()['error']['message'])
			return res
		except ValueError:
			print "Timeout"
			raise ThomsonException("Response timeout: " + res.text)

	@staticmethod
	def securityExpenseRatio(secList):
		'''
		secList should be structured as:
		[ (sec1, IdentifierType), (sec2, IdentifierType), ...]
		'''
		body = {
			'ExtractionRequest': {
				'@odata.type': '#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.TermsAndConditionsExtractionRequest',
				'ContentFieldNames': [
					'Total Expense Ratio Value',
					'Total Expense Ratio Date'
				],
				'IdentifierList':{
					'@odata.type': '#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.InstrumentIdentifierList',
					'InstrumentIdentifiers':
					[{'Identifier': s[0], 'IdentifierType': s[1]} for s in secList]
				}
			}
		}
		header = {
			'Prefer': 'respond-async',
			'Content-Type': 'application/json',
			'Authorization': Instance.token
		}

		res = requests.post(apiBase + 'Extractions/Extract', data=json.dumps(body), headers=header)
		try:
			if 'error' in res.json():
				raise ThomsonException(res.json()['error']['message'])
			return res 
		except ValueError:
			print "Timeout"
			raise ThomsonException("Response timeout: " + res.text)


	@staticmethod
	def fundAllocation(secList):
		'''
		secList should be structured as:
		[ (sec1, IdentifierType), (sec2, IdentifierType), ...]
		'''
		body = {
			'ExtractionRequest': {
				'@odata.type': '#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.FundAllocationExtractionRequest',
				'ContentFieldNames': [
					'Total Expense Ratio Value',
					'Fund Allocation'
				],
				'IdentifierList':{
					'@odata.type': '#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.InstrumentIdentifierList',
					'InstrumentIdentifiers':
					[{'Identifier': s[0], 'IdentifierType': s[1]} for s in secList]
				}
			}
		}
		header = {
			'Prefer':'respond-async',
			'Content-Type': 'application/json',
			'Authorization': Instance.token
		}

		res = requests.post(apiBase + 'Extractions/Extract', data=json.dumps(body), headers=header)
		try:
			if 'error' in res.json():
				raise ThomsonException(res.json()['error']['message'])
			return res
		except ValueError:
			print 'Timeout'
			raise ThomsonException('Response timeout: ' + res.text)