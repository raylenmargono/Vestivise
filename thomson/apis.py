import requests
import json
import datetime
from collections import deque
import numpy as np
import pandas as pd
from Vestivise.keys import tr_username, tr_password
"""
This module exists for the sake of contacting the Thomson Reuters Datascope API
and returning the necessary data in a format easily serialized for its usage
elsewhere in the program. In several instances, this will come in the form of
a pandas DataFrame, other formats will typically include dicts and lists.

Please refer to the docstrings of each specific function to see what they return.
"""
apiBase = 'https://hosted.datascopeapi.reuters.com/RestApi/v1/'


class ThomsonException(Exception):
    def __init__(self, dErrorArguments):
        Exception.__init__(self, dErrorArguments)


token = ''
lastKeyTime = datetime.datetime.now()


def requestToken():
    """
    Reaches out to the Thomson Reuters DataScope API to get a token to permit
    requests. Note that the username and password to get access are found in
    Vestivise/keys.py. This sets the global token on the module.

    If the token is null, or hasn't been updated within the last twelve hours,
    the current token will be eliminated and replaced with the result of a new
    request.
    """
    global token
    global lastKeyTime
    if (token and lastKeyTime > datetime.datetime.now() - datetime.timedelta(hours=12)):
        return
    print("Obtaining thomson auth token")
    header = {
        'Prefer': 'respond-async',
        'Content-Type': 'application/json'
    }
    body = {
        'Credentials': {
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
    """
    Accepts an in-progress response, and continues to check on it until the
    request has been completed, or the function times out.
    :param res: The request to be checked on.
    :return: A requests.response.
    """
    global token
    header = {
        'Prefer': 'respond-async',
        'Authorization': token
    }
    finishedRes = requests.get(res.headers['Location'], headers=header)
    while finishedRes.status_code == 202:
        finishedRes = requests.get(res.headers['Location'], headers=header)
    return finishedRes


def securityHistory(secList, startDate, endDate, dataFrame=False):
    """
    Reaches out to the Thomson Reuters DataScope API to obtain the Universal
    Close Price and the date corresponding to that price for each security
    listed in the first parameter (secList), for each date between the given
    interval in the second and third parameters (startDate, endDate). Should
    the fourth parameter be set to true (dataFrame), then the output will be
    a pandas.DataFrame of the content, indexed by date. Otherwise, the output
    will be a list of lists, each having touples of the price, and the date,
    sorted by the date, and the lists organized in the same order as the secList
    request.

    :param: secList : The list of all securities for which information will be
    gathered. Note that each security should be structured as its identifier,
    and then the type of identifier. For example,
    [('PFOAX.O', 'Ric'), ('56063U794', 'Cusip'), ('AAPL.OQ', 'Ric')]

    :param: startDate : The starting date for which data should be collected.
    Note that this value expects a datetime.date object, NOT a datetime.

    :param: endDate : The ending date for which data should be collected.
    Note that this value expects a datetime.date object, NOT a datetime.

    :param: dataFrame : Default set to False. Determines whether this function returns
    a pandas.DataFrame object, which it does on True, or a list of lists, which
    it does otherwise.
    """

    requestToken()
    global token
    body = {
        'ExtractionRequest': {
            '@odata.type': '#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.TimeSeriesExtractionRequest',
            'ContentFieldNames': [
                'Universal Close Price',
                'Trade Date'
            ],
            'IdentifierList': {
                '@odata.type': '#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.InstrumentIdentifierList',
                'InstrumentIdentifiers':
                    [{'Identifier': s[0], 'IdentifierType': s[1]} for s in secList],

            },
            'Condition': {
                'StartDate': str(startDate) + "T00:00:00.000Z",
                'EndDate': str(endDate) + "T00:00:00.000Z",
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
    # NOTE Alex please make this faster in the future.
    if not dataFrame:
        for ident in secList:
            tmpDeque = deque()
            for obj in data:
                if ident[0] == obj['Identifier']:
                    tmpDeque.appendleft((obj['Universal Close Price'], obj['Trade Date']))
            ret[ident[0]] = list(tmpDeque)
        size = max([len(ret[x]) for x in ret])
        for it in ret:
            ret[it] = ret[it] + [None] * (size - len(ret[it]))
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
            ret[item] = ret[item] + [None] * (len(indDeque) - len(ret[item]))
        df = pd.DataFrame(ret, index=pd.to_datetime(indDeque))
        return df[[x[0] for x in secList]]


def securityReturns(secList, startDate, endDate):
    """
    Returns a pandas.DataFrame containing the calculated returns over a period
    of time.
    :param: secList : The list of all securities for which information will be
    gathered. Note that each security should be structured as its identifier,
    and then the type of identifier. For example,
    [('PFOAX.O', 'Ric'), ('56063U794', 'Cusip'), ('AAPL.OQ', 'Ric')]

    :param: startDate : The starting date for which data should be collected.
    Note that this value expects a datetime.date object, NOT a datetime.

    :param: endDate : The ending date for which data should be collected.
    Note that this value expects a datetime.date object, NOT a datetime.

    :return:A pandas.DataFrame containing the calculated returns over the
    given period of time.
    """
    secPrices = securityHistory(secList, startDate, endDate, dataFrame=True)
    ret = pd.DataFrame(secPrices).pct_change()
    return ret


def sharpeRatio(secWeights, secList, startDate, endDate):
    """
    Calculates the Sharpe Ratio of a portfolio with historical info
    gathered over a given interval.

    :param secWeights: The list of weights of all securities that will be used
    in the computation. Note that these should be in the same order as the
    securities listed in secList.

    :param: secList : The list of all securities for which information will be
    gathered. Note that each security should be structured as its identifier,
    and then the type of identifier. For example,
    [('PFOAX.O', 'Ric'), ('56063U794', 'Cusip'), ('AAPL.OQ', 'Ric')]

    :param: startDate : The starting date for which data should be collected.
    Note that this value expects a datetime.date object, NOT a datetime.

    :param: endDate : The ending date for which data should be collected.
    Note that this value expects a datetime.date object, NOT a datetime.
    :return:
    """
    secReturns = securityReturns(secList, startDate, endDate)
    sigma = secReturns.cov()
    mu = secReturns.mean()

    rfrr = .33
    sr = (mu.dot(secWeights) - rfrr) / np.sqrt(sigma.dot(secWeights).dot(secWeights))
    return sr


def securityExpenseRatio(secList):
    """
    Gathers the expense ratios for a list of given securities.

    :param: secList : The list of all securities for which information will be
    gathered. Note that each security should be structured as its identifier,
    and then the type of identifier. For example,
    [('PFOAX.O', 'Ric'), ('56063U794', 'Cusip'), ('AAPL.OQ', 'Ric')]

    :return: A list of floating point values denoting the expense ratio for
    each requested security, in the same order as the requested securities.
    """
    requestToken()
    global token
    body = {
        'ExtractionRequest': {
            '@odata.type': '#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.TermsAndConditionsExtractionRequest',
            'ContentFieldNames': [
                'Total Expense Ratio Value',
                'Annual Management Charge'
            ],
            'IdentifierList': {
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
    """
    Gathers the fund allocation requested for a certain set of securities.

    :param: secList : The list of all securities for which information will be
    gathered. Note that each security should be structured as its identifier,
    and then the type of identifier. For example,
    [('PFOAX.O', 'Ric'), ('56063U794', 'Cusip'), ('AAPL.OQ', 'Ric')]

    :return:
    """

    requestToken()
    global token
    body = {
        'ExtractionRequest': {
            '@odata.type': '#ThomsonReuters.Dss.Api.Extractions.ExtractionRequests.FundAllocationExtractionRequest',
            'ContentFieldNames': [
                'Allocation Percentage',
                'Allocation Asset Type'
            ],
            'IdentifierList': {
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
        print 'Timeout'
        raise ThomsonException('Response timeout: ' + res.text)

    data = res.json()
    print(data['Notes'])
    data = data['Contents']

    return data
