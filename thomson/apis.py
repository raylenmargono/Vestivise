import requests
import json
import datetime
from collections import deque
import numpy as np
import pandas as pd
from Vestivise.keys import tr_username, tr_password

apiBase = 'https://hosted.datascopeapi.reuters.com/RestApi/v1/'

class ThomsonException(Exception):
	def __init__(self, dErrorArguments):
		Exception.__init__(self, dErrorArguments)

token  = ''
lastKeyTime = datetime.datetime.now()

def requestToken():
	global token
	global lastKeyTime
	if(token and lastKeyTime > datetime.datetime.now() - datetime.timedelta(hours=12)):
		return
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
		token = 'Token ' + res.json()['value']
	except ValueError:
		print "Timeout"
		print res.text

def getInProgress(res):
	global token
	header = {
		'Prefer': 'respond-async',
		'Authorization' : token
	}
	finishedRes = requests.get(res.headers['Location'], headers=header)
	while finishedRes.status_code == 202:
		finishedRes = requests.get(res.headers['Location'], headers=header)
	return finishedRes

def securityHistory(secList, startDate, endDate, dataFrame = False):
	'''
	secList should be structured as:
	[ (sec1, IdentifierType), (sec2, IdentifierType), ...]
	Also, note that startDate and endDate expect datetime.date
	objects, NOT datetimes.
	'''
	requestToken()
	global token
	body = {
		'ExtractionRequest': {
			'@odata.type': '#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.TimeSeriesExtractionRequest',
			'ContentFieldNames': [
				'Universal Close Price',
				'Trade Date'
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
		'Authorization': token
	}

	res = requests.post(apiBase + 'Extractions/ExtractWithNotes', data=json.dumps(body), headers=header)

	if res.status_code == 202:
		res = getInProgress(res)
	try:
		if 'error' in res.json():
			raise ThomsonException(res.json()['error']['message'])
	except ValueError:
		print(res.status_code)
		print res
		print "Timeout"
		raise ThomsonException("Response timeout: " + res.text)

	data = res.json()
	print(data['Notes'])
	data = data['Contents']
	ret = dict()
	#NOTE Alex please make this faster in the future.
	if not dataFrame:
		for ident in secList:
			tmpDeque = deque()
			for obj in data:
				if ident[0] == obj['Identifier']:
					tmpDeque.appendleft((obj['Universal Close Price'], obj['Trade Date']))
			ret[ident[0]] = list(tmpDeque)
		size = max([len(ret[x]) for x in ret])
		for it in ret:
			ret[it] = ret[it] + [None]*(size-len(ret[it]))
		return ret
	else:
		indDeque = deque()
		for ident in secList:
			tmpDeque = deque()
			for obj in data:
				if ident[0] == obj['Identifier']:
					tmpDeque.appendleft(obj['Universal Close Price'])
					if obj['Trade Date'] not in indDeque and obj['Trade Date']:
						indDeque.appendleft(obj['Trade Date'])
			ret[ident[0]] = list(tmpDeque)
		for item in ret:
			ret[item] = ret[item] + [None]*(len(indDeque) - len(ret[item]))
		df =  pd.DataFrame(ret, index=pd.to_datetime(indDeque))
		return df[[x[0] for x in secList]]

def securityReturns(secList, startDate, endDate):
	secPrices = securityHistory(secList, startDate, endDate, dataFrame = True)
	ret = pd.DataFrame(secPrices).pct_change()
	return ret

def sharpeRatio(secWeights, secList, startDate, endDate):
	secReturns = securityReturns(secList, startDate, endDate)
	sigma = secReturns.cov()
	mu = secReturns.mean()

	rfrr = .33
	sr = (mu.dot(secWeights) - rfrr) / sigma.dot(secWeights).dot(secWeights)
	return sr


def securityExpenseRatio(secList):
	'''
	secList should be structured as:
	[ (sec1, IdentifierType), (sec2, IdentifierType), ...]
	'''
	requestToken()
	global token
	body = {
		'ExtractionRequest': {
			'@odata.type': '#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.TermsAndConditionsExtractionRequest',
			'ContentFieldNames': [
				'Total Expense Ratio Value',
				'Annual Management Charge'
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
		'Authorization': token
	}

	res = requests.post(apiBase + 'Extractions/Extract', data=json.dumps(body), headers=header)
	if res.status_code == 202:
		res = getInProgress(res)
	try:
		jres = res.json()
		if 'error' in jres:
			raise ThomsonException(res.json()['error']['message'])
		expRatios = [x['Total Expense Ratio Value'] for x in jres['value']]
		return expRatios
	except ValueError:
		print "Timeout"
		raise ThomsonException("Response timeout: " + res.text)


def fundAllocation(secList):
	'''
	secList should be structured as:
	[ (sec1, IdentifierType), (sec2, IdentifierType), ...]
	'''
	requestToken()
	global token
	body = {
		'ExtractionRequest': {
			'@odata.type': '#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.FundAllocationExtractionRequest',
			'ContentFieldNames': [
				'Allocation Percentage',
				'Allocation Asset Type'
			],
			'IdentifierList':{
				'@odata.type': '#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.InstrumentIdentifierList',
				'InstrumentIdentifiers':
				[{'Identifier': s[0], 'IdentifierType': s[1]} for s in secList]
			},
			'Condition': {
				'FundAllocationTypes': ['FullHoldings']
			}
		}
	}
	header = {
		'Prefer':'respond-async',
		'Content-Type': 'application/json',
		'Authorization': token
	}

	res = requests.post(apiBase + 'Extractions/ExtractWithNotes', data=json.dumps(body), headers=header)
	if res.status_code == 202:
		res = getInProgress(res)
	try:
		if 'error' in res.json():
			raise ThomsonException(res.json()['error']['message'])

	except ValueError:
		print 'Timeout'
		raise ThomsonException('Response timeout: ' + res.text)

	data = res.json()
	print(data['Notes'])
	data = data['Contents']

	return data
