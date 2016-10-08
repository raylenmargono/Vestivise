import string
import dateutil.parser
import requests
from django.utils.datetime_safe import datetime
from numpy.random import random
import keys
import Vestivise
from django.utils import timezone


class QuovoRequestError(Exception):

    def __init__(self, message, *args):
        self.message = message
        super(QuovoRequestError, self).__init__(message, *args)


class _Quovo:

    def __init__(self):
        # The base API URL
        self.root = 'https://api.quovo.com/v2'
        # The access token used to authenticate API requests
        self.token = None
        self.username = keys.quovo_username
        self.password = keys.quovo_password


    def check_credentials(self):
        """Authenticates API user credentials. If the credentials are valid,
        the request will return any authentication tokens.
        """
        # Token authentication uses Basic Authorization to verify your API
        # user credentials.
        return self.__make_request('GET', '/tokens',
                                 auth=(self.username, self.password), token_auth=False)

    def create_user(self, email, name):
        """Creates a Quovo user.
        """
        params = {
            'username': email,
            'email' : email,
            'name' : name
        }
        return self.__make_request('POST', '/users', params=params)


    def create_account(self, user_id, brokerage_id, username, password):
        """Creates an account on the given user.
        """
        params = {
            'brokerage': brokerage_id,
            'username': username,
            'password': password
        }
        return self.__make_request('POST', '/users/{0}/accounts'.format(user_id), params=params)

    def get_sync_status(self, account_id):
        """Gets the current sync status on an account.
        """
        return self.__make_request('GET', '/accounts/{0}/sync'.format(account_id))

    def sync_account(self, account_id):
        """Initiates a sync on the given account.
        """
        return self.__make_request('POST', '/accounts/{0}/sync'.format(account_id))

    def get_account_portfolios(self, account_id):
        """Fetches all of an account's portfolios.
        """
        return self.__make_request('GET', '/accounts/{0}/portfolios'.format(account_id))

    def get_portfolio(self, portfolio_id):
        """Fetches a single portfolio.
        """
        return self.__make_request('GET', '/portfolios/{0}'.format(portfolio_id))

    def get_portfolio_positions(self, portfolio_id):
        """Fetches a portfolio's holdings or position data.
        """
        return self.__make_request('GET', '/portfolios/{0}/positions'.format(portfolio_id))

    def get_portfolio_history(self, portfolio_id):
        """Fetches a portfolio's available transaction history.
        """
        return self.__make_request('GET', '/portfolios/{0}/history'.format(portfolio_id))

    def set_token(self, token):
        self.token = token

    def __check_response_status(self, response):
        """Checks for a non-good status code.
        """
        if response.status_code not in (200, 201, 204):
            # This simply raises an Exception that is caught and handled in
            # the controller. You might use more robust handlers for non-good
            # response statuses, depending on the error.
            message = response.json()['message']
            raise QuovoRequestError(message, response)

    def token_is_valid(self):
        return dateutil.parser.parse(self.token['expiration']) > timezone.now()

    def __make_request(self, method, path, params=None, headers=None,
                       auth=None, token_auth=True):
        """A simple helper method/wrapper around all HTTP requests.
        """
        # To authenticate an API request, pass the appropriate Access Token in
        # the request header. This follows typical Bearer Token Authorization.

        if not self.token_is_valid(datetime.now()):
            try:
                token_response = self.__create_token()
                self.set_token(token_response)
            except QuovoRequestError as e:
                raise Vestivise.QuovoTokenErrorException(e.message)

        if token_auth and self.token:
            headers = {'Authorization': 'Bearer {0}'.format(self.token)}
        if method == "GET":
            response = requests.get(self.root + path, auth=auth,
                                    headers=headers, params=params)
        elif method == "POST":
            response = requests.post(self.root + path, auth=auth,
                                     headers=headers, params=params)
        self.__check_response_status(response)

        return response.json()

    def __create_token(self):
        """Creates a new Access Token.
        """
        name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        params = {'name': name}
        return self.__make_request('POST', '/tokens', params=params,
                                 auth=(self.username, self.password), token_auth=False)


Quovo = _Quovo()