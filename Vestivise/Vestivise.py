from django.http import JsonResponse
import logging

from rest_framework import renderers


def network_response(payload, **kwargs):
    status = 200

    if 'status' in kwargs:
        status = kwargs.get('status')

    return JsonResponse({
        'status': 'succcess',
        'data': payload if payload else ""
    }, status=status)


class VestivseRestRender(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_data = {}
        if data:
            if 'count' in data:
                response_data['count'] = data['count']
            if 'previous' in data:
                response_data['previous'] = data['previous']
            if 'next' in data:
                response_data['next'] = data['next']
            if 'results' in data:
                response_data['data'] = data['results']
            else:
                response_data['data'] = data
            response_data["status"] = "error"
            if renderer_context.get('response').status_code >= 200 and renderer_context.get('response').status_code < 300:
                response_data["status"] = "success"
        return super(VestivseRestRender, self).render(response_data, accepted_media_type, renderer_context)

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

class UserCreationResendException(VestiviseException):
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

class QuovoRequestError(VestiviseException):

    def __init__(self, message):
        VestiviseException.__init__(self, message, 400)

class NightlyProcessException(VestiviseException):

    def __init__(self, message):
        VestiviseException.__init__(self, message, 400)