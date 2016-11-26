from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
import data.algos
from django.http import Http404
from django.http import HttpResponseForbidden
from Vestivise import permission
from Vestivise.Vestivise import VestiviseException, QuovoWebhookException, network_response
from data.models import Holding
from dashboard.models import QuovoUser
from Vestivise import mailchimp
from tasks import task_nightly_process
import logging
import json


def holdingEditor(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    return render(request, "data/holdingEditorView.html")


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def testNightlyProcess(request):
    task_nightly_process()
    return network_response("success")


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

class HoldingSerializer(generics.ListAPIView):
    serializer_class = Holding
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        queryset = Holding.objects.all()

        completed = self.request.query_params.get('completed', None)
        if completed is not None:
            queryset = Holding.objects.filter(cusip__isnull=True)

        return queryset

class HoldingDetailView(generics.UpdateAPIView):
    serializer_class = Holding
    permission_classes = (IsAdminUser,)
    queryset = Holding.objects.all()


logger = logging.getLogger('quovo_sync')
# WEBHOOK FINISH SYNC
@api_view(['POST'])
@permission_classes((permission.QuovoWebHookPermission, ))
def finishSyncHandler(request):
    data = request.data
    user = data.get("user")
    user_id = user.get("id")
    logger.info("begin quovo sync logging: "  + json.dumps(request.data))
    if data.get("event") == "sync" and data.get("action") == "completed":
        try:
            handleNewQuovoSync(user_id)
        except VestiviseException as e:
            e.log_error()
            return e.generateErrorResponse()
    return network_response("")

def handleNewQuovoSync(quovo_id):
    try:
        vestivise_quovo_user = QuovoUser.objects.get(quovoID=quovo_id)
        # if the user has no current holdings it means that this is their first sync
        if not vestivise_quovo_user.didLink:
            logger.info("begin first time sync for: " + str(vestivise_quovo_user.id))
            holdings = vestivise_quovo_user.getNewHoldings()
            vestivise_quovo_user.setCurrentHoldings(holdings)
            email = vestivise_quovo_user.userProfile.user.email
            mailchimp.sendProcessingHoldingNotification(email)
    except QuovoUser.DoesNotExist:
        raise QuovoWebhookException("User {0} does not exist".format(quovo_id))
