import keys
import Vestivise
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
        self.root = "http://api.morningstar.com/v2/service"
        # The access token used to authenticate API requests.
        self.token = None
        self.username = keys.morningstar_username
        self.password = keys.morningstar_password

    def get_token(self):

    def __make_request(self, method, path, params=None, headers=None):
        """
        A simple helper method/wrapper around all HTTP requests.
        """
        try:
            token_response = self.__create_token()
            self.set_token(token_response)
        except MorningstarRequestError as e:
            raise Vestivise.MorningstarTokenErrorException(e.message)




