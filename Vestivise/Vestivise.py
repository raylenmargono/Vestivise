from django.http import JsonResponse

class VestErrors():

    #TODO need to log errors in this class

    @staticmethod
    def network_response(payload, **kwargs):

        status = 200

        if 'status' in kwargs:
            status = kwargs.get('status')

        return JsonResponse({
            'status': 'succcess',
            'data' : payload
        }, status=status)


    class VestiviseException(Exception):

        def __init__(self, message):
            self.message = message

        '''
        Accepts a VestiviseException and returns an error response according to the response
        @param exception: VestiviseException subclass
        '''
        @staticmethod
        def generateErrorResponse(exception):
            return JsonResponse({
                'error' : exception.error_message,
                'status' : 'error'
            }, status=exception.status)

    # NEW ERRORS HERE
    class CSVException(VestiviseException):

        def __init__(self, message):
            self.message = message
            self.status = 400
