import json
import dateutil.parser
from django.utils.datetime_safe import datetime
import requests
from Vestivise import keys, Vestivise

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
        self.auth_token = None
        self.auth_token_expiration = None
        self.username = keys.morningstar_username
        self.password = keys.morningstar_password

    def get_historical_nav(self, identifier, identifier_type, start_date, end_date):
        """
        Obtains the historical NAV values for some mutual fund, or other asset with value
        based on NAV.
        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :param start_date: Beginning date of the request. Should be datetime or datetime.date
        :param end_date: End date of the request. Should be datetime or datetime.date
        :return: List of small dictionaries consisting of the date, and the associated NAV value.
        """
        path = "service/mf/Price/{}/{}?startdate={}&enddate={}&format=json&accesscode={}".format(
            identifier_type, identifier, str(start_date).split(' ')[0],
            str(end_date).split(' ')[0], self.auth_token
        )
        data = self.__make_request('get', path)
        try:
            prices = data['data']['Prices']
        except KeyError as k:
            raise MorningstarRequestError("Desired information, \"{}\" wasn't present! Issue with identifier: {}"
                                          .format(k, identifier), data)
        return prices

    def get_historical_market_price(self, identifier, identifier_type, start_date, end_date):
        """
        Obtains the historical market price values for some publicly traded asset.
        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :param start_date: Beginning date of the request. Should be datetime or datetime.date
        :param end_date: End date of the request. Should be datetime or datetime.date
        :return: List of small dictionaries consisting of the date, and the associated LowPrice,
                HighPrice, OpenPrice, and ClosePrice.
        """
        path = "service/mf/MarketPrice/{}/{}?format=json&startdate={}&enddate={}&accesscode={}".format(
            identifier_type, identifier, str(start_date).split(' ')[0],
            str(end_date).split(' ')[0], self.auth_token
        )
        data = self.__make_request('get', path)
        try:
            prices = data['data']['MarketPrice']
        except KeyError as k:
            raise MorningstarRequestError("Desired information, \"{}\" wasn't present! Issue with identifier: {}"
                                          .format(k, identifier), data)
        return prices

    def get_prospectus_fees(self, identifier, identifier_type):
        """
        Obtains the prospectus fees of some security.
        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :return: Dictionary containing the security's ProspectusDate, ActualManagementFee,
                NetExpenseRatio, and GrossExpenseRatio.
        """
        path = "v2/service/mf/ProspectusFees/{}/{}?format=json&accesscode={}".format(
            identifier_type, identifier, self.auth_token
        )
        data = self.__make_request('get', path)
        try:
            if identifier_type.lower() == 'ticker':
                response = data['data'][0]['api']
            else:
                response = data['data']['api']
        except KeyError as k:
            raise MorningstarRequestError("Desired information, \"{}\" wasn't present! Issue with identifier: {}"
                                          .format(k, identifier), data)
        return response

    def get_historical_dividends(self, identifier, identifier_type, start_date, end_date):
        """
        Obtains the historical dividends of some given fund.
        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :param start_date: Beginning date of the request. Should be datetime or datetime.date
        :param end_date: End date of the request. Should be datetime or datetime.date
        :return: List of small dictionaries consisting of the date ('d'), the type of Dividend ('t'), and the
                associated value ('v').
        """

        path = "service/mf/DividendBreakdown/{}/{}?format=json&startdate={}&enddate={}&accesscode={}".format(
            identifier_type, identifier, str(start_date).split(' ')[0],
            str(end_date).split(' ')[0], self.auth_token
        )

        data = self.__make_request('get', path)
        try:
            dividends = data['data']['DividendBreakdown']
        except KeyError as k:
            raise MorningstarRequestError("Desired information \"{}\" wasn't present! Issue with identifier: {}"
                                          .format(k, identifier), data)
        return dividends

    def get_historical_distributions(self, identifier, identifier_type, start_date, end_date):
        """
        Obtains the historical distributions of some given fund.
        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :param start_date: Beginning date of the request. Should be datetime or datetime.date
        :param end_date: End date of the request. Should be datetime or datetime.date
        :return: Dictionary containing the HistoricalDistributions and CapitalGainDetails.
        """
        path = "service/mf/HistoricalDistributions/{}/{}?format=json&startdate={}&enddate={}&accesscode={}".format(
            identifier_type, identifier, str(start_date).split(' ')[0],
            str(end_date).split(' ')[0], self.auth_token
        )

        data = self.__make_request('get', path)
        try:
            dists = data['data']['HistoricalDistributions']
        except KeyError as k:
            raise MorningstarRequestError("Desired information \"{}\" wasn't present! Issue with identifier: {}"
                                          .format(k, identifier), data)
        return dists

    def get_asset_allocation(self, identifier, identifier_type):
        """
        Obtains the asset allocation breakdown for the most recent, publicly
        available portfolio date.

        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :return: Dictionary containing the percentage allocation to a certain
                asset, with the asset category as keyname. Refer to Morningstar
                documentation for asset categories.
        """
        path = "v2/service/mf/AssetAllocationBreakdownRecentPort/{}/{}?format=json&accesscode={}".format(
            identifier_type, identifier, self.auth_token
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

    def get_equity_breakdown(self, identifier, identifier_type):
        """
        Obtains the equity breakdown for the most recent, publicly available
        portfolio date.

        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :return: Dictionary containing the percentage allocation to a certain
                equity sector.
        """
        path = "v2/service/mf/GlobalStockSectorBreakdown/{}/{}?format=json&accesscode={}".format(
            identifier_type, identifier, self.auth_token
        )
        data = self.__make_request('get', path)
        try:
            if identifier_type.lower() == 'ticker':
                response = data['data'][0]['api']
            else:
                response = data['data']['api']
        except (KeyError, IndexError) as k:
            raise MorningstarRequestError("Desired information \"{}\" wasn't present! Issue with identifier: {}"
                                          .format(k, identifier), data)
        return response

    def get_bond_breakdown(self, identifier, identifier_type):
        """
        Obtains the bond breakdown for the most recent, publicly available
        porfolio date.

        :param identifier: String identifier of the security.
        :param identifier_type: Type of identifier. eg: cusip, ticker, etc.
        :return: Dictionary containing the percentage allocation to a certain
                equity sector.
        """
        path = "v2/service/mf/GlobalBondSector/{}/{}?format=json&accesscode={}".format(
            identifier_type, identifier, self.auth_token
        )
        data = self.__make_request('get', path)
        try:
            if identifier_type.lower() == 'ticker':
                response = data['data'][0]['api']
            else:
                response = data['data']['api']
        except (KeyError, IndexError) as k:
            raise MorningstarRequestError("Desired information \"{}\" wasn't present! Issue with identifier: {}"
                                          .format(k, identifier), data)
        return response

    def get_asset_returns(self, identifier, identifier_type):
        """
        Returns the one year, two year, and three year returns for any
        asset according to Morningstar.
        :param identifier: String identifier of the security.
        :param identifier_type:Type of the identifier. eg: cusip, ticker, etc.
        :return: Dictionary containing the monthly percentage return over the course
                 of one year, two years, and three years.
        """
        path = "v2/service/mf/TrailingTotalReturn/{}/{}?format=json&accesscode={}&currency=CU$$$$$USD".format(
            identifier_type, identifier, self.auth_token
        )
        data = self.__make_request('get', path)
        try:
            if identifier_type.lower() == "ticker":
                response = data['data'][0]['api']
            else:
                response = data['data']['api']
        except (KeyError, IndexError) as k:
            raise MorningstarRequestError("Desired information \"{}\" wasn't present! Issue with identifier {}"
                                          .format(k, identifier), data)
        return response

    def __create_auth_token(self, days=90):
        """
        Creates a new Access Token.
        """
        path = "v2/service/account/CreateAccesscode/{}d?format=json&account_code={}&account_password={}".format(
            days, self.username, self.password
        )
        res = requests.get(self.root + path)
        if res.status_code == requests.codes.ok and res.json()['status']['code'] == 0:
            return res
        message = res.json()['status']['message']
        raise MorningstarRequestError(message, res)

    def set_auth_token(self, token_response):
        data = token_response.json()['data']['api']
        self.auth_token = data['AccessCode']
        self.auth_token_expiration = dateutil.parser.parse(data['ExpireTime'])

    def token_is_valid(self):
        return self.auth_token_expiration > datetime.now()

    def __make_request(self, method, path, params=None, headers=None, attempt=0):
        """
        A simple helper method/wrapper around all HTTP requests.
        """
        if attempt == 10:
            raise MorningstarRequestError("Maximum number of attempts (10) reached, could not access MS servers.")
        if not (self.auth_token and self.token_is_valid()):
            try:
                token_response = self.__create_auth_token()
                self.set_auth_token(token_response)
                path = path.rsplit("accesscode=")[0] + "accesscode=" + self.auth_token
            except MorningstarRequestError as e:
                raise Vestivise.MorningstarTokenErrorException(e.message)
            except (requests.Timeout, requests.ConnectionError):
                return self.__make_request(method, path, params=params, headers=headers, attempt=attempt+1)
        response = None
        try:
            if method == 'GET' or method == 'get':
                response = requests.get(self.root + path, headers=headers, data=params)
            elif method == 'POST' or method == 'post':
                response = requests.post(self.root + path, headers=headers, data=params)
        except (requests.Timeout, requests.ConnectionError):
            return self.__make_request(method, path, params=params, headers=headers, attempt=attempt+1)

        if response.status_code != requests.codes.ok:
            if attempt < 10:
                return self.__make_request(method, path, params=params, headers=headers, attempt=attempt + 1)
            try:
                message = response.json()['status']['message']
                raise MorningstarRequestError(message, response)
            except Exception:
                raise MorningstarRequestError("Something went wrong! Did you put the arguments"
                                              " in the correct order?", 404)

        try:
            ret = json.loads(response.text.replace("{}", ""))
        except ValueError:
            return self.__make_request(method, path, params=params, headers=headers, attempt=attempt+1)
        return ret

Morningstar = _Morningstar()
