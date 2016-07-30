from django.shortcuts import render
from django.http import Http404
from rest_framework.decorators import api_view
from django.http import JsonResponse
from data.models import *
from account.models import *
import data.algos

'''
BROKER FUNCTION:
Imput the request with the name of the module,
redirect the request to the module in question
and return the output of that module, however it
is organized.

NOTES/QUESTIONS:
Currently, I'm thinking the Broker is only 
for GET requests. A post request is issued 
along with the user/their credentials/the
module name, and any updates that are 
necessary are handled within the data app
before returning the necessary components
for the module. I'm not currently seeing 
any position where we have to post anything
to the broker. If I'm wrong about this,
let me know. -- ALEX

TODO:
-Verify if user has permissions to get the
 module they are requesting. 

-Determine if Ray wants it structured like this
 or if he would rather that it's structured for
 internal calls instead of /api/data/... calls.

-Better error handling.
'''
def broker(request, module):
	if not request.user.is_authenticated():
		raise Http404("Please Log In before using data API")
	module = module
	if hasattr(data.algos, module):
		method = getattr(data.algos, module)
		return method(request)
	else:
		raise Http404("Module not found")
