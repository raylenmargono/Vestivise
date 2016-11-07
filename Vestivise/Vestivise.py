from django.http import JsonResponse
import logging

def network_response(payload, **kwargs):
    status = 200

    if 'status' in kwargs:
        status = kwargs.get('status')

    return JsonResponse({
        'status': 'succcess',
        'data': payload
    }, status=status)


class VestiviseException(Exception):

    def __init__(self, message, status):

        self.message = message
        self.status = status

    def log_error(self):
        logger = logging.getLogger('vestivise_exception')
        logger.exception(self.message, exc_info=True)

    def generateErrorResponse(self):
        """
        Accepts a VestiviseException and returns an error response according to the response
        @param exception: VestiviseException subclass
        """
        return JsonResponse({
            'error' : self.message,
            'status' : 'error'
        }, status=self.status)

    # NEW ERRORS HERE


class CSVException(VestiviseException):
    def __init__(self, message):
        VestiviseException.__init__(self, message, 400)


class LoginException(VestiviseException):
    def __init__(self, message):
        VestiviseException.__init__(self, message, 400)


class UserCreationException(VestiviseException):
    def __init__(self, message):
        VestiviseException.__init__(self, message, 400)


class QuovoTokenErrorException(VestiviseException):
    def __init__(self, message):
        VestiviseException.__init__(self, message, 400)


class MorningstarTokenErrorException(VestiviseException):
    def __init__(self, message):
        VestiviseException.__init__(self, message, 400)


class UnidentifiedHoldingException(VestiviseException):
    def __init__(self, message):
        VestiviseException.__init__(self, message, 400)

class QuovoEmptyQuestionAnswer(VestiviseException):
    def __init__(self, message):
        VestiviseException.__init__(self, message, 400)

class QuovoWebhookException(VestiviseException):
    def __init__(self, message):
        VestiviseException.__init__(self, message, 400)