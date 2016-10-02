from django.core.mail import send_mail
from django.shortcuts import render
import data.algos
from django.http import Http404
from django.http import HttpResponseForbidden


def holdingEditor(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    return render(request, "data/holdingEditorView.html")


def broker(request, module):
    """
    Gets the output of the requested module.
    :param request: The request to be forwarded to the module algorithm.
    :param module: The name of the desired module algorithm.
    :return: The response produced by the desired module algorithm.
    """
    if not request.user.is_authenticated() and not "Test" in module:
        raise Http404("Please Log In before using data API")
    module = module
    if hasattr(data.algos, module):
        method = getattr(data.algos, module)
        return method(request)
    else:
        raise Http404("Module not found")


# EMAIL TASKS
def alertIdentifyHoldings(holding_name):
    send_mail(
        'Missing Holding',
        holding_name,
        'danger@vestivise.com',
        ['raylen@vestivise.com', 'alex@vestivise.com', 'josh@vestivise.com'],
        fail_silently=False,
    )
