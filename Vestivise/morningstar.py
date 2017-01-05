import keys
import Vestivise
from django.utils.datetime_safe import datetime
from requests.packages.urllib3.connection import NewConnectionError
import dateutil.parser
import requests
"""
This module acts to obtain financial information directly from the
Morningstar API, and returns the desired information for use in
module computations.
"""

class MorningstarRequestError(Exception):

    def __init__(self, message, *args):
        self.message = message
        super(MorningstarRequestError, self).__init__(message, *args)


class _Morningstar:

    def __init__(self):
        # Base API URL
        self.root = "http://api.morningstar.com/"
        # The access token used to authenticate API requests.
        self.authToken = None
        self.authTokenExpiration = None
        self.username = keys.morningstar_username
        self.password = keys.morningstar_password

    def getHistoricalNAV(self, identifier, identifier_type, start_date, end_date):
        """
        Obtains the historical NAV values for some mutual fund, or other asset with value
        based on NAV.
        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :param start_date: Beginning date of the request. Should be datetime or datetime.date
        :param end_date: End date of the request. Should be datetime or datetime.date
        :return: List of small dictionaries consisting of the date, and the associated NAV value.
        """
        path = "service/mf/Price/{0}/{1}?startdate={2}&enddate={3}&format=json&accesscode={4}".format(
            identifier_type, identifier, str(start_date).split(' ')[0],
            str(end_date).split(' ')[0], self.authToken
        )
        data = self.__make_request('get', path)
        try:
            prices = data['data']['Prices']
        except KeyError as k:
            raise MorningstarRequestError("Desired information, \"{0}\" wasn't present! Issue with identifier: {1}"
                                          .format(k, identifier), data)
        return prices

    def getHistoricalMarketPrice(self, identifier, identifier_type, start_date, end_date):
        """
        Obtains the historical market price values for some publicly traded asset.
        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :param start_date: Beginning date of the request. Should be datetime or datetime.date
        :param end_date: End date of the request. Should be datetime or datetime.date
        :return: List of small dictionaries consisting of the date, and the associated LowPrice,
                HighPrice, OpenPrice, and ClosePrice.
        """
        path = "service/mf/MarketPrice/{0}/{1}?format=json&startdate={2}&enddate={3}&accesscode={4}".format(
            identifier_type, identifier, str(start_date).split(' ')[0],
            str(end_date).split(' ')[0], self.authToken
        )
        data = self.__make_request('get', path)
        try:
            prices = data['data']['MarketPrice']
        except KeyError as k:
            raise MorningstarRequestError("Desired information, \"{0}\" wasn't present! Issue with identifier: {1}"
                                          .format(k, identifier), data)
        return prices

    def getProspectusFees(self, identifier, identifier_type):
        """
        Obtains the prospectus fees of some security.
        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :return: Dictionary containing the security's ProspectusDate, ActualManagementFee,
                NetExpenseRatio, and GrossExpenseRatio.
        """
        path = "v2/service/mf/ProspectusFees/{0}/{1}?format=json&accesscode={2}".format(
            identifier_type, identifier, self.authToken
        )
        data = self.__make_request('get', path)
        try:
            if identifier_type.lower() == 'ticker':
                response = data['data'][0]['api']
            else:
                response = data['data']['api']
        except KeyError as k:
            raise MorningstarRequestError("Desired information, \"{0}\" wasn't present! Issue with identifier: {1}"
                                          .format(k, identifier), data)
        return response

    def getHistoricalDividends(self, identifier, identifier_type, start_date, end_date):
        """
        Obtains the historical dividends of some given fund.
        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :param start_date: Beginning date of the request. Should be datetime or datetime.date
        :param end_date: End date of the request. Should be datetime or datetime.date
        :return: List of small dictionaries consisting of the date ('d'), the type of Dividend ('t'), and the
                associated value ('v').
        """

        path = "service/mf/DividendBreakdown/{0}/{1}?format=json&startdate={2}&enddate={3}&accesscode={4}".format(
            identifier_type, identifier, str(start_date).split(' ')[0],
            str(end_date).split(' ')[0], self.authToken
        )

        data = self.__make_request('get', path)
        try:
            dividends = data['data']['DividendBreakdown']
        except KeyError as k:
            raise MorningstarRequestError("Desired information \"{0}\" wasn't present! Issue with identifier: {1}"
                                          .format(k, identifier), data)
        return dividends

    def getAssetAllocation(self, identifier, identifier_type):
        """
        Obtains the asset allocation breakdown for the most recent, publicly
        available portfolio date.

        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :return: Dictionary containing the percentage allocation to a certain
                asset, with the asset category as keyname. Refer to Morningstar
                documentation for asset categories.
        """
        path = "v2/service/mf/AssetAllocationBreakdownRecentPort/{0}/{1}?format=json&accesscode={2}".format(
            identifier_type, identifier, self.authToken
        )
        data = self.__make_request('get', path)
        try:
            if identifier_type.lower() == 'ticker':
                response = data['data'][0]['api']
            else:
                response = data['data']['api']
        except (KeyError, IndexError) as k:
            raise MorningstarRequestError("Desired information, \"{0}\" wasn't present! Issue with identifier: {1}"
                                          .format(k, identifier), data)
        return response

    def getEquityBreakdown(self, identifier, identifier_type):
        """
        Obtains the equity breakdown for the most recent, publicly available
        portfolio date.

        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :return: Dictionary containing the percentage allocation to a certain
                equity sector.
        """
        path = "v2/service/mf/GlobalStockSectorBreakdown/{0}/{1}?format=json&accesscode={2}".format(
            identifier_type, identifier, self.authToken
        )
        data = self.__make_request('get', path)
        try:
            if identifier_type.lower() == 'ticker':
                response = data['data'][0]['api']
            else:
                response = data['data']['api']
        except (KeyError, IndexError) as k:
            raise MorningstarRequestError("Desired information \"{0}\" wasn't present! Issue with identifier: {1}"
                                          .format(k, identifier), data)
        return response

    def getBondBreakdown(self, identifier, identifier_type):
        """
        Obtains the bond breakdown for the most recent, publicly available
        porfolio date.

        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :return: Dictionary containing the percentage allocation to a certain
                equity sector.
        """
        path = "v2/service/mf/GlobalBondSector/{0}/{1}?format=json&accesscode={2}".format(
            identifier_type, identifier, self.authToken
        )
        data = self.__make_request('get', path)
        try:
            if identifier_type.lower() == 'ticker':
                response = data['data'][0]['api']
            else:
                response = data['data']['api']
        except (KeyError, IndexError) as k:
            raise MorningstarRequestError("Desired information \"{0}\" wasn't present! Issue with identifier: {1}"
                                          .format(k, identifier), data)
        return response

    def getAssetReturns(self, identifier, identifier_type):
        """
        Returns the one year, two year, and three year returns for any
        asset according to Morningstar.
        :param identifier: String identifier of the security.
        :param identifier_type:Type of the identifier. eg: cusip, ticker, etc.
        :return: Dictionary containing the monthly percentage return over the course
                 of one year, two years, and three years.
        """
        path = "v2/service/mf/TrailingTotalReturn/{0}/{1}?format=json&accesscode={2}&currency=CU$$$$$USD".format(
            identifier_type, identifier, self.authToken
        )
        data = self.__make_request('get', path)
        try:
            if identifier_type.lower() == "ticker":
                response = data['data'][0]['api']
            else:
                response = data['data']['api']
        except (KeyError, IndexError) as k:
            raise MorningstarRequestError("Desired information \"{0}\" wasn't present! Issue with identifier {!}"
                                          .format(k, identifier), data)
        return response

    def __create_authToken(self, days=90):
        """
        Creates a new Access Token.
        """
        path = "v2/service/account/CreateAccesscode/{0}d?format=json&account_code={1}&account_password={2}".format(
            days, self.username, self.password
        )
        res = requests.get(self.root + path)
        if res.status_code == requests.codes.ok and res.json()['status']['code'] == 0:
            return res
        message = res.json()['status']['message']
        raise MorningstarRequestError(message, res)

    def set_authToken(self, tokenResponse):
        data = tokenResponse.json()['data']['api']
        self.authToken = data['AccessCode']
        self.authTokenExpiration = dateutil.parser.parse(data['ExpireTime'])

    def token_is_valid(self):
        return self.authTokenExpiration > datetime.now()

    def __make_request(self, method, path, params=None, headers=None, attempt=0):
        """
        A simple helper method/wrapper around all HTTP requests.
        """
        if not (self.authToken and self.token_is_valid()):
            try:
                token_response = self.__create_authToken()
                self.set_authToken(token_response)
                path = path.rsplit("accesscode=")[0] + "accesscode=" + self.authToken
            except MorningstarRequestError as e:
                raise Vestivise.MorningstarTokenErrorException(e.message)
            except NewConnectionError as e:
                if attempt == 10:
                    raise MorningstarRequestError("Maximum number of attempts (10) reached, could not access MS servers.")
                return self.__make_request(method, path, params=params, headers=headers, attempt=attempt+1)

        if method == 'GET' or method == 'get':
            response = requests.get(self.root + path, headers=headers, data=params)
        elif method == 'POST' or method == 'post':
            response = requests.post(self.root + path, headers=headers, data=params)

        if response.status_code != requests.codes.ok:
            try:
                message = response.json()['status']['message']
                raise MorningstarRequestError(message, response)
            except Exception as e:
                raise MorningstarRequestError("Something went wrong! Did you put the arguments"
                                              " in the correct order?", 404)

        return response.json()


Morningstar = _Morningstar()





