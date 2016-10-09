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

    def __init__(self, message, status, name):
        if not name:
            raise Exception("VestiviseException requires __name__ as second parameter")
        self.message = message
        self.status = status
        logger = logging.getLogger(name)
        print name
        logger.error("test")
        logger.exception(message)

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
    def __init__(self, message, name):
        VestiviseException.__init__(self, message, 400, name)


class LoginException(VestiviseException):
    def __init__(self, message, name):
        VestiviseException.__init__(self, message, 400, name)


class UserCreationException(VestiviseException):
    def __init__(self, message, name):
        VestiviseException.__init__(self, message, 400, name)


class QuovoTokenErrorException(VestiviseException):
    def __init__(self, message, name):
        VestiviseException.__init__(self, message, 400, name)
