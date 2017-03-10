import os
from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
import data.algos
from django.http import Http404
from django.http import HttpResponseForbidden
from Vestivise import permission
from Vestivise import settings
from Vestivise.Vestivise import VestiviseException, QuovoWebhookException, network_response
from data.models import Holding, Account
from dashboard.models import QuovoUser, ProgressTracker
from Vestivise import mailchimp
from tasks import task_nightly_process, task_instant_link
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

@api_view(["GET"])
def demoBroker(request, module):
    jsonFile = open(os.path.join(settings.BASE_DIR, 'data/fixtures/demoData.json'))
    demo_data = json.loads(jsonFile.read())
    if not demo_data.get(module):
        raise Http404
    return network_response(demo_data.get(module))

@api_view(["GET"])
@permission_classes((IsAuthenticated, permission.QuovoAccountPermission))
def broker(request, module):
    """
    Gets the output of the requested module.
    :param request: The request to be forwarded to the module algorithm.
    :param module: The name of the desired module algorithm.
    :param filters: The account fitlers to be excluded from calculations.
    :return: The response produced by the desired module algorithm.
    """
    if not request.user.is_authenticated():
        raise Http404("Please Log In before using data API")
    module = module
    if hasattr(data.algos, module):
        filters = request.GET.getlist('filters')
        if filters:
            ProgressTracker.track_progress(request.user, {"track_id" : "total_filters"})
        quovo_ids_exclude = request.user.profile.quovoUser.userAccounts.filter(active=True).filter(id__in=filters).values_list("quovoID", flat=True)
        method = getattr(data.algos, module)
        r = method(request, acctIgnore=quovo_ids_exclude)
        return r
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
    account = data.get("account")
    account_id = account.get("id")
    logger.info("begin quovo sync logging: " + json.dumps(request.data))
    if data.get("action") == "completed" and data.get('sync').get('status') == 'good':
        if data.get("event") == "sync":
            try:
                handleNewQuovoSync(user_id, account_id)
            except VestiviseException as e:
                e.log_error()
                return e.generateErrorResponse()
    if data.get("action") == "deleted":
        try:
            handleQuovoDelete(account_id, user_id)
        except Account.DoesNotExist:
            pass
    return network_response("")


def handleNewQuovoSync(quovo_id, account_id):
    vestivise_quovo_user = QuovoUser.objects.get(quovoID=quovo_id)
    email = vestivise_quovo_user.userProfile.user.email
    mailchimp.sendProcessingHoldingNotification(email)
    # if the user has no current holdings it means that this is their first sync
    if not Account.objects.filter(quovoID=account_id):
        user = get_user_model().objects.get(profile__quovoUser__quovoID=923393)
        ProgressTracker.track_progress(user, {"track_id":"did_link"})
        task_instant_link(quovo_id, account_id)


def handleQuovoDelete(account_id, quovo_id):
    a = Account.objects.get(quovoID=account_id)
    a.delete()
    vestivise_quovo_user = QuovoUser.objects.get(quovoID=quovo_id)
    if vestivise_quovo_user.userAccounts.exists():
        vestivise_quovo_user.getUserReturns()
        vestivise_quovo_user.getUserSharpe()
        vestivise_quovo_user.getUserBondEquity()
